import os
import json
import argparse
import time
import random
from openai import OpenAI
from httpx import HTTPStatusError

LOG_FILE = "tts_log.jsonl"

# Load prompts
with open("tts_prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

TASKS = list(PROMPTS.keys())
OPENAI_VOICES = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'nova', 'onyx', 'sage', 'shimmer']

client = OpenAI()

MAX_REQUESTS_PER_MIN = 500
MAX_RETRIES = 5

def rate_limit_pause(last_minute_requests, start_minute):
    """Pause if RPM exceed limit."""
    if last_minute_requests >= MAX_REQUESTS_PER_MIN:
        elapsed = time.time() - start_minute
        if elapsed < 60:
            wait = 60 - elapsed
            print(f"[RATE LIMIT] Sleeping {wait:.1f}s to respect 500 RPM...")
            time.sleep(wait)
        return 0, time.time()
    return last_minute_requests, start_minute


def query_openai(style, script, output_path, model='gpt-4o-mini-tts', voice='alloy'):
    """Send query to OpenAI TTS API with retry + backoff."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=script,
                instructions=style
            ) as response:
                response.stream_to_file(output_path)
            return True
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = (2 ** retries) + random.uniform(0, 1)
                print(f"[429] Rate limited. Retry in {wait:.1f}s...")
                time.sleep(wait)
                retries += 1
            else:
                print(f"[ERROR] HTTP {e.response.status_code}: {e}")
                return False
        except Exception as e:
            wait = (2 ** retries) + random.uniform(0, 1)
            print(f"[ERROR] {e}. Retry in {wait:.1f}s...")
            time.sleep(wait)
            retries += 1
    print(f"[FAIL] Gave up after {MAX_RETRIES} retries for {output_path}")
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
    """Append a completed sample record to the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def generate_samples(task, output_dir, completed):
    """Generate TTS samples for a given task with 500 RPM limit + resume."""
    if task not in PROMPTS:
        raise ValueError(f"Task '{task}' not found in prompts file.")

    task_data = PROMPTS[task]

    last_minute_requests = 0
    start_minute = time.time()

    for subtask, examples in task_data.items():
        for i, ex in enumerate(examples):
            style = ex.get("style", "")
            script = ex["script"]
            voice = ex.get("voice", "alloy")

            filename = f"{task}_{subtask}_{i}.wav"
            output_path = os.path.join(output_dir, filename)

            if filename in completed and os.path.exists(output_path):
                print(f"[SKIP] Already completed: {filename}")
                continue

            # Throttle if hitting 500 RPM
            last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)

            print(f"[INFO] Generating {task}/{subtask} → {filename}")
            success = query_openai(style, script, output_path, voice=voice)

            if success:
                log_completion({
                    "task": task,
                    "subtask": subtask,
                    "index": i,
                    "style": style,
                    "script": script,
                    "voice": voice,
                    "filename": filename,
                    "path": output_path
                })
                last_minute_requests += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="test", choices=TASKS + ["all"],
                        help="The name of the generation task, or 'all' for all tasks.")
    parser.add_argument("--output", type=str, default="./outputs", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    completed = load_completed()

    if args.task == "all":
        for t in TASKS:
            print(f"\n=== Processing task: {t} ===")
            generate_samples(t, args.output, completed)
    else:
        generate_samples(args.task, args.output, completed)
