import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from gpt_prompt_templates import TASK_TEMPLATES

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

# def process_response(task_data, subtask, message):
#     """Assumes the returned message is already a JSON of required form"""
#     try:
#         new_examples = json.loads(message)
#         if isinstance(new_examples, list):
#             task_data[subtask].extend(new_examples)
#         else:
#             task_data[subtask].append(new_examples)
#     except Exception as e:
#         print(f'Could not parse GPT output for {subtask}: {e}')
#         print('Raw GPT output:', message)

def process_response_script(task_data, subtask, example, message):
    """Assumes the returned message is a JSON array of scripts only"""
    try:
        scripts = json.loads(message)
        if not isinstance(scripts, list):
            raise ValueError("Expected a JSON array of strings.")
        
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
    try:
        utterances = json.loads(message)
        if not isinstance(utterances, list):
            raise ValueError("Expected a JSON array of strings.")
        
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

def save_extended(extended_prompts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extended_prompts, f, indent=4)
    print(f'Saved extended prompts to {output_file}')


# def extend_general_task(task_name, num_per_subcategory, prompts):
#     """Extend a single-utterance QA task where subtasks correspond to labels."""
#     if task_name not in prompts:
#         raise ValueError(f"Task '{task_name}' not found in {INPUT_FILE}")

#     task_data = prompts[task_name]
#     task_prompt = task_data['prompt']

#     for subtask, examples in task_data.items():
#         if subtask == 'prompt':
#             continue
        
#         # Show GPT one example in the correct JSON format
#         example_json = json.dumps(examples[0], indent=4)
#         label = examples[0].get('label', subtask)
#         pretended = examples[0].get('pretended', '')

#         print(f'Extending {task_name}/{subtask} with {num_per_subcategory} new samples...')

#         user_msg = TASK_TEMPLATES['general'].format(
#             task_name=task_name,
#             subtask=subtask,
#             task_prompt=task_prompt,
#             label=label,
#             pretended=pretended,
#             examples=example_json,
#             num=num_per_subcategory
#         )

#         message = query(user_msg)
#         print('GPT Output:\n', message)
#         process_response(task_data, subtask, message)

#     return prompts


def extend_general_task(task_name, num_per_subcategory, prompts, target_subtask=None):
    if task_name not in prompts:
        raise ValueError(f"Task '{task_name}' not found in {INPUT_FILE}")

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

# def extend_signal_task(task_name, num_per_subcategory, prompts):
#     if task_name not in prompts:
#         raise ValueError(f"Task '{task_name}' not found in {INPUT_FILE}")

#     task_data = prompts[task_name]

#     for subtask, examples in task_data.items():
#         if subtask == 'prompt':
#             continue
        
#         print(f'Extending {task_name}/{subtask} with {num_per_subcategory} new samples')

#         system_msg = TASK_TEMPLATES[task_name]['system']
#         user_msg = TASK_TEMPLATES[task_name]['user'].format(
#             num=num_per_subcategory,
#             label=examples[0]['label'],
#             pretend=examples[0]['pretend'],
#             example_script=examples[0]['script']
#         )

#         message = query(system_msg, user_msg)
#         print('GPT Output:\n', message)
#         process_response_script(task_data, subtask, examples[0]['pretend'], message)

#     return prompts

def extend_counting_task(num_new_subtasks, prompts):
    """Generate multiple counting subtasks in one GPT call."""
    task_name = 'counting'
    task_data = prompts[task_name]
    task_prompt = task_data['prompt']

    # Show GPT a sample of existing examples
    
    
    example = {
        "pretend": task_data['0']['pretend'],
        "scripts": [entry['script'] for entry in task_data['0']['dialogue']]
    }
    # sample_subtasks = {k: task_data[k] for k in list(task_data.keys()) if k != 'prompt'} 
    example_json = json.dumps(example, indent=4)

    # Compute the next available index
    existing_indices = [int(k) for k in task_data.keys() if k != 'prompt']
    start_index = max(existing_indices) + 1 if existing_indices else 0

    print(f'Extending {task_name} with {num_new_subtasks} new samples starting from index {start_index}')

    system_msg = TASK_TEMPLATES[task_name]['system']
    user_msg = TASK_TEMPLATES[task_name]['user'].format(
        # task_name=task_name,
        # task_prompt=task_prompt,
        actual=len(example['scripts']),
        pretend=example['pretend'],
        example=example_json,
        num=num_new_subtasks,
        # start_index=start_index
    )

    message = query(system_msg, user_msg)
    print('GPT Output:\n', message)
    # process_response_dialogue()

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, required=True, help='The task to extend (e.g., age, volume, pitch, speed, emotion, counting).')
    parser.add_argument('--subtask', type=str, default=None, help='Optional: Only extend this subtask instead of all subtasks.')
    parser.add_argument('--n', type=int, default=1, help='Number of new contrastive examples')
    args = parser.parse_args()

    # output_file = f'tts_prompts_{args.task}_extended.json'
    output_file = INPUT_FILE

    # Load tts_prompts.json
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    if args.task == 'counting':
        prompts = extend_counting_task(args.n, prompts)
    elif args.task == 'accent':
        prompts = extend_accent_task(args.n, prompts, target_subtask=args.subtask)
    elif args.task in ['age', 'gender', 'volume', 'range', 'speed', 'pitch', 'intonation']:
        prompts = extend_general_task(args.task, args.n, prompts, target_subtask=args.subtask)
    else:
        raise NotImplementedError(f'task {args.task} not implemented.')

    save_extended(prompts, output_file)
