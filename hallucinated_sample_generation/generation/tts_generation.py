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
import wave

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

LOG_FILE = 'tts_log.jsonl'

# Load prompts
with open('tts_prompts.json', 'r', encoding='utf-8') as f:
    PROMPTS = json.load(f)

TASKS = list(PROMPTS.keys())
OPENAI_VOICES = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer', 'verse']
OPENAI_FEMALE_VOICES = ['alloy', 'coral', 'nova', 'sage', 'shimmer']
OPENAI_MALE_VOICES = ['ash', 'ballad', 'echo', 'fable', 'onyx', 'verse']

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
eleven_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

MAX_REQUESTS_PER_MIN = 500
MAX_RETRIES = 5

local_tmp_dir = './tmp'
os.makedirs(local_tmp_dir, exist_ok=True)

def rate_limit_pause(last_minute_requests, start_minute):
    """Pause if requests/minute exceed limit."""
    if last_minute_requests >= MAX_REQUESTS_PER_MIN:
        elapsed = time.time() - start_minute
        if elapsed < 60:
            wait = 60 - elapsed
            print(f'Sleeping {wait:.1f}s to respect 500 RPM...')
            time.sleep(wait)
        return 0, time.time()
    return last_minute_requests, start_minute

def query_elevenlabs(script, output_path, voice_id, model='eleven_turbo_v2_5'):
    """Query ElevenLabs TTS API."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = eleven_client.text_to_speech.convert(
                voice_id=voice_id,
                output_format='pcm_16000',
                text=script,
                model_id=model,
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=True,
                    speed=1.0,
                ),
            )

            pcm_bytes = b''.join(chunk for chunk in response if chunk)
            if not pcm_bytes:
                print(f'No audio returned for {output_path}')
                return False
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)         # mono
                wav_file.setsampwidth(2)         # 16-bit
                wav_file.setframerate(16000)     # 16000 sr
                wav_file.writeframes(pcm_bytes)

            return True
        except Exception as e:
            wait = (2 ** retries) + random.uniform(0, 1)
            print(f'ElevenLabs ERR: {e}. Retry in {wait:.1f}s...')
            time.sleep(wait)
            retries += 1
    print(f'Gave up after {MAX_RETRIES} retries for {output_path}')
    return False

def query_openai(style, script, output_path, model='gpt-4o-mini-tts', voice='alloy'):
    """Query OpenAI TTS API."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            with openai_client.audio.speech.with_streaming_response.create(
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
                print(f'Rate limited. Retry in {wait:.1f}s...')
                time.sleep(wait)
                retries += 1
            else:
                print(f'HTTP ERR: {e.response.status_code}: {e}')
                return False
        except Exception as e:
            wait = (2 ** retries) + random.uniform(0, 1)
            print(f'ERR: {e}. Retry in {wait:.1f}s...')
            time.sleep(wait)
            retries += 1
    print(f'Gave up after {MAX_RETRIES} retries for {output_path}')
    return False


def load_completed():
    """Load previously completed samples from log file."""
    completed = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    completed.add(record['filename'])
                except json.JSONDecodeError:
                    continue
    return completed


def log_completion(record):
    """Append sample record to the log file."""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')

# def filter_verified_voices(voices, expected_filters):
#     """Filter ElevenLabs voices by verifying their labels against expected filters."""
#     verified = []
#     for voice in voices:
#         labels = {k.lower(): voice.labels.get(k, '').lower() for k in voice.labels}
#         match = all(labels.get(key, '') == value.lower() 
#                     for key, value in expected_filters.items())
#         if match:
#             verified.append(voice)
#         else:
#             print(f'Skipping {voice.name} ({voice.voice_id}) — labels={labels}, expected={expected_filters}')
#     return verified

def get_verified_elevenlabs_voices(search, expected_filters=None, n_voices=30):
    """Fetch up to n_voices ElevenLabs voices that match expected_filters."""
    voices = []
    next_page_token = None
    expected_filters = {k.lower(): v.lower() for k, v in (expected_filters or {}).items()}

    try:
        while len(voices) < n_voices:
            response = eleven_client.voices.search(
                search=search,
                next_page_token=next_page_token
            )
            if not response.voices:
                break  # no more voices

            for voice in response.voices:
                labels = {k.lower(): voice.labels.get(k, '').lower() for k in voice.labels}
                if all(labels.get(key, '') == value for key, value in expected_filters.items()):
                    voices.append(voice)
                    if len(voices) >= n_voices:
                        break
                else:
                    print(f'Skipping {voice.name} ({voice.voice_id}) — labels={labels}, expected={expected_filters}')

            if not response.has_more or not response.next_page_token:
                break
            next_page_token = response.next_page_token

        return voices
    except Exception as e:
        print(f'11labs error: {e}')
        return []

def generate_samples_elevenlabs(task, output_dir, completed, last_minute_requests, start_minute):
    """TTS generation with 11labs for tasks age/gender/accent."""
    task_data = PROMPTS[task]
    prompt = task_data.get('prompt', '')

    # voices = get_elevenlabs_voices()
    # if not voices:
    #     print('No ElevenLabs voices available.')
    #     return last_minute_requests, start_minute

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        print(f'Processing 11labs task {task} subtask {subtask}')
        for i, ex in enumerate(examples):
            style = ex['style']
            script = ex['script']
            label = ex['label']

            voices = get_verified_elevenlabs_voices(search=subtask, expected_filters={task: subtask})
            if not voices:
                print(f'No 11labs voices for task {task}, subtask {subtask}')
                continue

            for v in voices:
                filename = f'{task}_{subtask}_{i}_{v.voice_id}.wav'
                output_path = os.path.join(output_dir, filename)

                if filename in completed and os.path.exists(output_path):
                    print(f'Skipping. Already completed: {filename}')
                    continue

                last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)
                print(f'Generating with ElevenLabs voice {v.name} ({v.voice_id}) to {filename}')
                success = query_elevenlabs(script, output_path, voice_id=v.voice_id)

                if success:
                    log_completion({
                        'task': task,
                        'subtask': subtask,
                        'index': i,
                        'prompt': prompt,
                        'label': label,
                        'style': style,
                        'script': script,
                        'voice': v.voice_id,
                        'filename': filename,
                        'path': output_path
                    })
                    last_minute_requests += 1
    return last_minute_requests, start_minute

def generate_samples_default(task, output_dir, completed, last_minute_requests, start_minute):
    """Default TTS generation (non-dialogue tasks)."""
    task_data = PROMPTS[task]
    prompt = task_data.get('prompt', '')

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        print(f'Processing default task {task} subtask {subtask}')
        for i, ex in enumerate(examples):
            voice_spec = ex['voice']
            style = ex['style']
            script = ex['script']
            label = ex['label']

            if voice_spec == 'all':
                voices = OPENAI_VOICES
            elif voice_spec == 'openai_female':
                voices = OPENAI_FEMALE_VOICES
            elif voice_spec == 'openai_male':
                voices = OPENAI_MALE_VOICES
            else:
                voices = [voice_spec]

            for voice in voices:
                filename = f'{task}_{subtask}_{i}_{voice}.wav'
                output_path = os.path.join(output_dir, filename)

                if filename in completed and os.path.exists(output_path):
                    print(f'Skipping. Already completed: {filename}')
                    continue

                last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)
                print(f'Generating {task}/{subtask} ({voice}) to {filename}')
                success = query_openai(style, script, output_path, voice=voice)

                if success:
                    log_completion({
                        'task': task,
                        'subtask': subtask,
                        'index': i,
                        'prompt': prompt,
                        'label': label,
                        'style': style,
                        'script': script,
                        'voice': voice,
                        'filename': filename,
                        'path': output_path
                    })
                    last_minute_requests += 1
    return last_minute_requests, start_minute


def generate_samples_dialogue(task, output_dir, completed, last_minute_requests, start_minute):
    """Dialogue TTS generation (concatenate all voices per subtask)."""
    task_data = PROMPTS[task]
    prompt = task_data.get('prompt', '')

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        out_file = os.path.join(output_dir, f'{task}_{subtask}.wav')
        if os.path.basename(out_file) in completed and os.path.exists(out_file):
            print(f'Skipping. Already completed: {out_file}')
            continue

        print(f'Processing dialogue task {task} subtask {subtask}')
        
        clips = []
        voices = set()

        for i, ex in enumerate(examples):
            voice = ex['voice']
            style = ex['style']
            script = ex['script']

            voices.add(voice)

            temp_file = os.path.join(local_tmp_dir, f'{task}_{subtask}_{i}_{voice}.wav')
            
            # if os.path.basename(temp_file) in completed and os.path.exists(temp_file):
            #     print(f'Skipping. Already completed: {temp_file}')
            # else:
            last_minute_requests, start_minute = rate_limit_pause(last_minute_requests, start_minute)
            print(f'Generating dialogue clip: {task}/{subtask} ({voice})')
            success = query_openai(style, script, temp_file, voice=voice)

            if success:
                # log_completion({
                #     'task': task,
                #     'subtask': subtask,
                #     'index': i,
                #     'prompt': prompt,
                #     'label': label,
                #     'style': style,
                #     'script': script,
                #     'voice': voice,
                #     'filename': os.path.basename(temp_file),
                #     'path': temp_file
                # })
                last_minute_requests += 1
            clips.append(temp_file)

        if clips:
            combined = AudioSegment.silent(duration=200)
            for clip in clips:
                audio = AudioSegment.from_file(clip)
                combined += audio + AudioSegment.silent(duration=250)
            combined.export(out_file, format='wav')
            print(f'Concatenated {len(clips)} clips to {out_file}')
            if task == 'counting':
                label = len(voices)
            log_completion({
                'task': task,
                'subtask': subtask,
                'prompt': prompt,
                'label': label,  # default label = number of speakers
                'voice': [ex['voice'] for ex in examples],
                'script': [ex['script'] for ex in examples],
                'style': [ex['style'] for ex in examples],
                'filename': os.path.basename(out_file),
                'path': out_file
            })

    return last_minute_requests, start_minute

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', nargs='+', default=['test'], choices=TASKS + ['all'], help="List of generation tasks or 'all'")
    parser.add_argument('--output', type=str, default='./tts_outputs', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    completed = load_completed()

    last_minute_requests = 0
    start_minute = time.time()

    if 'all' in args.tasks:
        selected_tasks = TASKS
    else:
        selected_tasks = args.tasks

    for t in selected_tasks:
        if t in ['age', 'gender', 'accent']:
            last_minute_requests, start_minute = generate_samples_elevenlabs(t, args.output, completed, last_minute_requests, start_minute)
        elif t == 'counting':
            last_minute_requests, start_minute = generate_samples_dialogue(t, args.output, completed, last_minute_requests, start_minute)
        else:
            last_minute_requests, start_minute = generate_samples_default(t, args.output, completed, last_minute_requests, start_minute)
           