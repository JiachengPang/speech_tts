import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from gpt_prompt_templates import TASK_TEMPLATES

import random
random.seed(42)

import re

from utils_logging import setup_logger
setup_logger('gpt_prompt_generation')

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

INPUT_FILE = 'tts_prompts_base.json'

def query(system_msg, user_msg):
    print('=================================================')
    print(system_msg)
    print('-------------------------------------------------')
    print(user_msg)
    print('=================================================')
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_msg},
        ],
        temperature=0.9
    )

    message = response.choices[0].message.content.strip()
    return message

def process_response_script(task_data, subtask, example, message):
    """Assumes the returned message is a JSON array of scripts only"""
    try:
        scripts = json.loads(message)
        if not isinstance(scripts, list):
            raise ValueError('Expected a JSON array of strings.')
        
        for script in scripts:
            new_example = {
                'voice': example['voice'],
                'style': example['style'],
                'script': script,
                'label': example['label'],
                'pretend': example['pretend']
            }
            task_data[subtask].append(new_example)
    except Exception as e:
        print(f'Cannot parse GPT output for {subtask}: {e}')
        print(f'Raw output: {message}')

def process_response_accent(task_data, subtask, example, message):
    """Assumes the returned JSON is an array of objects {'script':..., 'pretend':...}"""
    try:
        utterances = json.loads(message)
        if not isinstance(utterances, list):
            raise ValueError('Expected a JSON array of strings.')
        
        for utterance in utterances:
            new_example = {
                'voice': example['voice'],
                'style': example['style'],
                'script': utterance['script'],
                'label': example['label'],
                'pretend': utterance['pretend']
            }
            task_data[subtask].append(new_example)
    except Exception as e:
        print(f'Cannot parse GPT output for {subtask}: {e}')
        print(f'Raw output: {message}')

def extend_general_task(task_name, num_per_subcategory, prompts, target_subtask=None):
    if task_name not in prompts:
        raise ValueError(f'Task "{task_name}" not found in {INPUT_FILE}')

    task_data = prompts[task_name]

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        if target_subtask and subtask != target_subtask:
            continue
        
        print(f'Extending {task_name}/{subtask} with {num_per_subcategory} new samples')

        system_msg = TASK_TEMPLATES[task_name]['system']
        user_msg = TASK_TEMPLATES[task_name]['user'].format(
            num=num_per_subcategory,
            label=examples[0]['label'],
            pretend=examples[0]['pretend'],
            example_script=examples[0]['script']
        )

        message = query(system_msg, user_msg)
        print('GPT Output:\n', message)
        process_response_script(task_data, subtask, examples[0], message)

    return prompts

def extend_accent_task(num_per_subcategory, prompts, target_subtask=None):
    accents = ['american', 'british']
    task_name = 'accent'
    
    task_data = prompts[task_name]

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        if target_subtask and subtask != target_subtask:
            continue
        
        print(f'Extending {task_name}/{subtask} with {num_per_subcategory} new samples')

        example = {
            'script': examples[0]['script'],
            'pretend': examples[0]['pretend']
        }
        system_msg = TASK_TEMPLATES[task_name]['system']
        user_msg = TASK_TEMPLATES[task_name]['user'].format(
            num=num_per_subcategory,
            label=examples[0]['label'],
            example_object=example
        )

        message = query(system_msg, user_msg)
        print('GPT Output:\n', message)
        process_response_accent(task_data, subtask, examples[0], message)

    return prompts

def next_available_index(task_data):
    existing_indices = [int(k) for k in task_data.keys() if k != 'prompt']
    return max(existing_indices) + 1 if existing_indices else 0

def extend_counting_task(num_new_subtasks, prompts):
    """Generate multiple counting subtasks in one GPT call."""
    task_name = 'counting'
    task_data = prompts[task_name]

    # Show GPT a sample of existing examples
    example = {
        'pretend': task_data['0']['pretend'],
        'scripts': [entry['script'] for entry in task_data['0']['dialogue']]
    }
    example_json = json.dumps(example, indent=4)

    start_index = next_available_index(task_data)

    print(f'Extending {task_name} with {num_new_subtasks} new samples starting from index {start_index}')

    system_msg = TASK_TEMPLATES[task_name]['system']
    user_msg = TASK_TEMPLATES[task_name]['user'].format(
        actual=len(example['scripts']),
        pretend=example['pretend'],
        example=example_json,
        num=num_new_subtasks
    )

    message = query(system_msg, user_msg)
    print('GPT Output:\n', message)

    try:
        new_subtasks = json.loads(message)
        if isinstance(new_subtasks, dict):
            task_data.update(new_subtasks)
        else:
            raise ValueError('Expected GPT to return a JSON object mapping indices to arrays.')
    except Exception as e:
        print(f'Could not parse GPT output for counting batch: {e}')
        print('Raw GPT output:', message)

    return prompts


def decap_first(s: str) -> str:
    """Lowercase the first alphabetic letter unless the first word is I or I'.."""
    m = re.search(r"[A-Za-z]", s)
    if not m:
        return s
    i = m.start()
    tail = s[i:]  # starts at first alpha
    # keep I / I'm / I'll / I’d etc.
    if re.match(r"^I($|\s|['’](m|ll|d|ve|re|s)\b)", tail):
        return s
    return s[:i] + s[i].lower() + s[i+1:]

def add_pause_after_word(script, pause, pause_time='1s'):
    """insert <break time=X/> after the word label_pause in script"""
    pattern = re.compile(rf'\b({re.escape(pause)})\b', flags=re.IGNORECASE)
    return pattern.sub(rf"\1 <break time='{pause_time}'/>", script, count=1)

def process_response_pause(task_data, message, start_index):
    try:
        utterances = json.loads(message)
        if not isinstance(utterances, list):
            raise ValueError('Expected GPT to return a JSON arary.')
        
        idx = start_index
        for u in utterances:
            script = u.get('script', '').strip()
            pauses = u.get('pauses', [])

            if not script or not isinstance(pauses, list) or len(pauses) < 2:
                continue
            
            # randomly choose two pause locations for pretend and label
            pretend_pause, label_pause = random.sample(pauses, 2)
            
            # insert pause after label_pause to style
            style = add_pause_after_word(script, label_pause)

            # prefix both
            style = f'I will pause after the word {pretend_pause}, and {decap_first(style)}'
            script = f'I will pause after the word {pretend_pause}, and {decap_first(script)}'
            
            task_data[str(idx)] = {
                'voice': '',
                'style': style,
                'script': script,
                'label': label_pause,
                'pretend': pretend_pause
            }
            idx += 1
            
    except Exception as e:
        print(f'Could not parse GPT output for ssml task {e}')
        print('Raw GPT output:', message)

def add_prolong_for_word(script, label_text, fast_rate='+30%', slow_rate='-100%'):
    """wrap word with slow rate, rest with fast rate"""
    # allow multi-word phrases
    pattern = re.compile(rf"\b({re.escape(label_text)})\b", flags=re.IGNORECASE)
    m = pattern.search(script)
    
    pre  = script[:m.start()]
    word = m.group(1)
    post = script[m.end():]

    parts = []
    if pre:
        parts.append(f"<prosody rate='{fast_rate}'>{pre}</prosody>")
    parts.append(f"<prosody rate='{slow_rate}'>{word}</prosody>")
    if post:
        parts.append(f"<prosody rate='{fast_rate}'>{post}</prosody>")

    return "".join(parts)

def process_response_prolong(task_data, message, start_index):
    try:
        utterances = json.loads(message)
        if not isinstance(utterances, list):
            raise ValueError('Expected GPT to return a JSON arary.')
        
        idx = start_index
        for u in utterances:
            script = u.get('script', '').strip()
            prolonged = u.get('prolonged', [])

            if not script or not isinstance(prolonged, list) or len(prolonged) < 2:
                continue
            
            # randomly choose two prolonged words for pretend and label
            pretend_prolong, label_prolong = random.sample(prolonged, 2)
            
            # prefix
            script = f'I will prolong the word {pretend_prolong}, and {decap_first(script)}'
            
            # style
            style = add_prolong_for_word(script, label_prolong)
            
            task_data[str(idx)] = {
                'voice': '',
                'style': style,
                'script': script,
                'label': label_prolong,
                'pretend': pretend_prolong
            }
            idx += 1
            
    except Exception as e:
        print(f'Could not parse GPT output for ssml task {e}')
        print('Raw GPT output:', message)

def add_stress_for_word(
        script, 
        label_text, 
        fast_rate='+20%', 
        slow_rate='-30%', 
        pitch='+20%', 
        # neighbor_volume='x-soft', 
        target_volume='x-loud', 
        # neighbor_emphasis='reduced',
        post_pause_time='150ms'):
    """wrap word with emphasis (slower, higher pitch, higher volume)"""
    # allow multi-word phrases
    pattern = re.compile(rf"\b({re.escape(label_text)})\b", flags=re.IGNORECASE)
    m = pattern.search(script)
    
    pre  = script[:m.start()]
    word = m.group(1)
    post = script[m.end():]

    parts = []

    # if pre:
    #     parts.append(
    #         f"<emphasis level='{neighbor_emphasis}'>"
    #         f"<prosody volume='{neighbor_volume}' rate='{fast_rate}'>{pre}</prosody>"
    #         f"</emphasis>"
    #     )

    # parts.append(
    #     f"<prosody pitch='{pitch}' volume='{target_volume}' rate='{slow_rate}'>{word}</prosody><break time='{post_pause_time}'/>"
    # )

    # if post:
    #     parts.append(
    #         f"<emphasis level='{neighbor_emphasis}'>"
    #         f"<prosody volume='{neighbor_volume}' rate='{fast_rate}'>{post}</prosody>"
    #         f"</emphasis>"
    #     )


    if pre:
        parts.append(
            f"<prosody rate='{fast_rate}'>{pre}</prosody>"
        )

    parts.append(
        f"<prosody pitch='{pitch}' volume='{target_volume}' rate='{slow_rate}'>{word}</prosody><break time='{post_pause_time}'/>"
    )

    if post:
        parts.append(
            f"<prosody rate='{fast_rate}'>{post}</prosody>"
        )

    return "".join(parts)

def process_response_stress(task_data, message, start_index):
    try:
        utterances = json.loads(message)
        if not isinstance(utterances, list):
            raise ValueError('Expected GPT to return a JSON arary.')
        
        idx = start_index
        for u in utterances:
            script = u.get('script', '').strip()
            stressed = u.get('stressed', [])

            if not script or not isinstance(stressed, list) or len(stressed) < 2:
                continue
            
            # randomly choose two stressed words for pretend and label
            pretend_stressed, label_stressed = random.sample(stressed, 2)
            
            # prefix
            script = f'I will stress the word {pretend_stressed}, and {decap_first(script)}'
            
            # style
            style = add_stress_for_word(script, label_stressed)
            
            task_data[str(idx)] = {
                'voice': '',
                'style': style,
                'script': script,
                'label': label_stressed,
                'pretend': pretend_stressed
            }
            idx += 1
            
    except Exception as e:
        print(f'Could not parse GPT output for ssml task {e}')
        print('Raw GPT output:', message)


def extend_ssml_task(task_name, num_new_subtasks, prompts):
    if task_name not in prompts:
        raise ValueError(f'Task "{task_name}" not found in {INPUT_FILE}')

    task_data = prompts[task_name]
    start_index = next_available_index(task_data)

    print(f'Extending {task_name} with {num_new_subtasks} new samples starting from index {start_index}')

    system_msg = TASK_TEMPLATES[task_name]['system']
    user_msg = TASK_TEMPLATES[task_name]['user'].format(
        num=num_new_subtasks
    )

    message = query(system_msg, user_msg)
    print('GPT Output:\n', message)
    if task_name == 'pause':
        process_response_pause(task_data, message, start_index)
    elif task_name == 'prolong':
        process_response_prolong(task_data, message, start_index)
    elif task_name == 'stress':
        process_response_stress(task_data, message, start_index)

    return prompts

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, required=True, help='The task to extend (e.g., age, volume, pitch, speed, emotion, counting).')
    parser.add_argument('--subtask', type=str, default=None, help='Optional: Only extend this subtask instead of all subtasks.')
    parser.add_argument('--n', type=int, default=1, help='Number of new contrastive examples')
    args = parser.parse_args()

    # output_file = f'tts_prompts_{args.task}_extended.json'
    output_file = INPUT_FILE

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    if args.task == 'counting':
        prompts = extend_counting_task(args.n, prompts)
    elif args.task == 'accent':
        prompts = extend_accent_task(args.n, prompts, target_subtask=args.subtask)
    elif args.task in ['pause', 'prolong', 'stress']:
        prompts = extend_ssml_task(args.task, args.n, prompts)
    elif args.task in ['age', 'gender', 'volume', 'range', 'speed', 'pitch', 'intonation']:
        prompts = extend_general_task(args.task, args.n, prompts, target_subtask=args.subtask)
    else:
        raise NotImplementedError(f'task {args.task} not implemented.')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=4)
    print(f'Saved extended prompts to {output_file}')
