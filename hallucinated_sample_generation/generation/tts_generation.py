import os
import json
import argparse
import time
import random
from openai import OpenAI
from httpx import HTTPStatusError

from dotenv import load_dotenv
load_dotenv()

from pydub import AudioSegment

LOG_FILE = "tts_log.jsonl"

# Load prompts
with open("tts_prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

TASKS = list(PROMPTS.keys())
OPENAI_VOICES = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer', 'verse']
OPENAI_FEMALE_VOICES = ['alloy', 'coral', 'nova', 'sage', 'shimmer']
OPENAI_MALE_VOICES = ['ash', 'ballad', 'echo', 'fable', 'onyx', 'verse']

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_REQUESTS_PER_MIN = 500
MAX_RETRIES = 5

local_tmp_dir = "./tmp"
os.makedirs(local_tmp_dir, exist_ok=True)

def rate_limit_pause(last_minute_requests, start_minute):
    """Pause if requests/minute exceed limit."""
    if last_minute_requests >= MAX_REQUESTS_PER_MIN:
        elapsed = time.time() - start_minute
        if elapsed < 60:
            wait = 60 - elapsed
            print(f"Sleeping {wait:.1f}s to respect 500 RPM...")
            time.sleep(wait)
        return 0, time.time()
    return last_minute_requests, start_minute


def query_openai(style, script, output_path, model='gpt-4o-mini-tts', voice='alloy'):
    """Query OpenAI TTS API with retry + backoff."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=script,
                instructions=style,
            ) as response:
                response.stream_to_file(output_path)
            return True
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = (2 ** retries) + random.uniform(0, 1)
                print(f"Rate limited. Retry in {wait:.1f}s...")
                time.sleep(wait)
                retries += 1
            else:
                print(f"HTTP ERR: {e.response.status_code}: {e}")
                return False
        except Exception as e:
            wait = (2 ** retries) + random.uniform(0, 1)
            print(f"ERR: {e}. Retry in {wait:.1f}s...")
            time.sleep(wait)
            retries += 1
    print(f"Gave up after {MAX_RETRIES} retries for {output_path}")
    return False


def load_completed():
    """Load previously completed samples from log file."""
    completed = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    completed.add(record["filename"])
                except json.JSONDecodeError:
                    continue
    return completed


def log_completion(record):
    """Append sample record to the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def generate_samples_default(task, output_dir, completed, last_minute_requests, start_minute):
    """Default TTS generation (non-dialogue tasks)."""
    task_data = PROMPTS[task]
    prompt = task_data.get("prompt", "")

    for subtask, examples in task_data.items():
        if subtask == "prompt":
            continue
        print(f"Processing default task {task} subtask {subtask}")
        for i, ex in enumerate(examples):
            voice_spec = ex['voice']
            style = ex["style"]
            script = ex["script"]
            label = ex["label"]

            if voice_spec == 'all':
                voices = OPENAI_VOICES
            elif voice_spec == 'openai_female':
                voices = OPENAI_FEMALE_VOICES
            elif voice_spec == 'openai_male':
                voices = OPENAI_MALE_VOICES
            else:
                voices = [voice_spec]

            for voice in voices:
                filename = f"{task}_{subtask}_{i}_{voice}.wav"
                output_path = os.path.join(output_dir, filename)

                if filename in completed and os.path.exists(output_path):
                    print(f"Skipping. Already completed: {filename}")
                    continue

                last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)
                print(f"Generating {task}/{subtask} ({voice}) to {filename}")
                success = query_openai(style, script, output_path, voice=voice)

                if success:
                    log_completion({
                        "task": task,
                        "subtask": subtask,
                        "index": i,
                        "prompt": prompt,
                        "label": label,
                        "style": style,
                        "script": script,
                        "voice": voice,
                        "filename": filename,
                        "path": output_path
                    })
                    last_minute_requests += 1
    return last_minute_requests, start_minute


def generate_samples_dialogue(task, output_dir, completed, last_minute_requests, start_minute):
    """Dialogue TTS generation (concatenate all voices per subtask)."""
    task_data = PROMPTS[task]
    prompt = task_data.get("prompt", "")

    for subtask, examples in task_data.items():
        if subtask == "prompt":
            continue
        out_file = os.path.join(output_dir, f"{task}_{subtask}.wav")
        if os.path.basename(out_file) in completed and os.path.exists(out_file):
            print(f"Skipping. Already completed: {out_file}")
            continue

        print(f"Processing dialogue task {task} subtask {subtask}")
        
        clips = []
        voices = set()

        for i, ex in enumerate(examples):
            voice = ex["voice"]
            style = ex["style"]
            script = ex["script"]

            voices.add(voice)

            temp_file = os.path.join(local_tmp_dir, f"{task}_{subtask}_{i}_{voice}.wav")
            
            # if os.path.basename(temp_file) in completed and os.path.exists(temp_file):
            #     print(f"Skipping. Already completed: {temp_file}")
            # else:
            last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)
            print(f"Generating dialogue clip: {task}/{subtask} ({voice})")
            success = query_openai(style, script, temp_file, voice=voice)

            if success:
                # log_completion({
                #     "task": task,
                #     "subtask": subtask,
                #     "index": i,
                #     "prompt": prompt,
                #     "label": label,
                #     "style": style,
                #     "script": script,
                #     "voice": voice,
                #     "filename": os.path.basename(temp_file),
                #     "path": temp_file
                # })
                last_minute_requests += 1
            clips.append(temp_file)

        if clips:
            combined = AudioSegment.silent(duration=200)
            for clip in clips:
                audio = AudioSegment.from_file(clip)
                combined += audio + AudioSegment.silent(duration=250)
            combined.export(out_file, format="wav")
            print(f"Concatenated {len(clips)} clips to {out_file}")
            if task == 'counting':
                label = len(voices)
            log_completion({
                "task": task,
                "subtask": subtask,
                "prompt": prompt,
                "label": label,  # default label = number of speakers
                "voice": [ex["voice"] for ex in examples],
                "script": [ex["script"] for ex in examples],
                "style": [ex["style"] for ex in examples],
                "filename": os.path.basename(out_file),
                "path": out_file
            })

    return last_minute_requests, start_minute

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="test", choices=TASKS + ["all"],
                        help="The name of the generation task, or 'all' for all tasks.")
    parser.add_argument("--output", type=str, default="./tts_outputs", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    completed = load_completed()

    last_minute_requests = 0
    start_minute = time.time()

    if args.task == "all":
        for t in TASKS:
            if t == "counting":  # dialogue mode
                last_minute_requests, start_minute = generate_samples_dialogue(t, args.output, completed, last_minute_requests, start_minute)
            else:  # default mode
                last_minute_requests, start_minute = generate_samples_default(t, args.output, completed, last_minute_requests, start_minute)
    else:
        if args.task == "counting":
            generate_samples_dialogue(args.task, args.output, completed, last_minute_requests, start_minute)
        else:
            generate_samples_default(args.task, args.output, completed, last_minute_requests, start_minute)