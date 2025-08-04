import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from gpt_prompt_templates import SYSTEM_MSG, TASK_TEMPLATES

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

INPUT_FILE = 'tts_prompts_base.json'

def query(user_msg):
    print('=================================================')
    print(user_msg)
    print('=================================================')
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': SYSTEM_MSG},
            {'role': 'user', 'content': user_msg},
        ],
        temperature=0.9
    )

    message = response.choices[0].message.content.strip()
    return message

def process_response(task_data, subtask, message):
    try:
        new_examples = json.loads(message)
        if isinstance(new_examples, list):
            task_data[subtask].extend(new_examples)
        else:
            task_data[subtask].append(new_examples)
    except Exception as e:
        print(f'Could not parse GPT output for {subtask}: {e}')
        print('Raw GPT output:', message)

def save_extended(extended_prompts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extended_prompts, f, indent=4)
    print(f'Saved extended prompts to {output_file}')


def extend_general_task(task_name, num_per_subcategory, prompts):
    """Extend a single-utterance QA task where subtasks correspond to labels."""
    if task_name not in prompts:
        raise ValueError(f"Task '{task_name}' not found in {INPUT_FILE}")

    task_data = prompts[task_name]
    task_prompt = task_data['prompt']

    for subtask, examples in task_data.items():
        if subtask == 'prompt':
            continue
        
        # Show GPT one example in the correct JSON format
        example_json = json.dumps(examples[0], indent=4)
        label = examples[0].get('label', subtask)  # for these tasks, subtask itself is the label
        pretended = examples[0].get('pretended', '')

        print(f'Extending {task_name}/{subtask} with {num_per_subcategory} new samples...')

        user_msg = TASK_TEMPLATES['general'].format(
            task_name=task_name,
            subtask=subtask,
            task_prompt=task_prompt,
            label=label,
            pretended=pretended,
            examples=example_json,
            num=num_per_subcategory
        )

        message = query(user_msg)
        print('GPT Output:\n', message)
        process_response(task_data, subtask, message)

    return prompts

def extend_counting_task(num_new_subtasks, prompts):
    """Generate multiple counting subtasks in one GPT call."""
    task_name = 'counting'
    task_data = prompts[task_name]
    task_prompt = task_data['prompt']

    # Show GPT a sample of existing examples
    example = task_data['0']
    # sample_subtasks = {k: task_data[k] for k in list(task_data.keys()) if k != 'prompt'} 
    example_json = json.dumps(example, indent=4)

    # Compute the next available index
    existing_indices = [int(k) for k in task_data.keys() if k != 'prompt']
    start_index = max(existing_indices) + 1 if existing_indices else 0

    print(f'Extending {task_name} with {num_new_subtasks} new samples...')

    user_msg = TASK_TEMPLATES[task_name].format(
        task_name=task_name,
        task_prompt=task_prompt,
        examples=example_json,
        num=num_new_subtasks,
        start_index=start_index
    )

    message = query(user_msg)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, required=True,
                        help='The task to extend (e.g., age, volume, pitch, speed, emotion, counting).')
    parser.add_argument('--n', type=int, default=1,
                        help='Number of new contrastive examples (per subtask for general tasks, '
                             'or total new subtasks for counting).')
    args = parser.parse_args()

    output_file = f'tts_prompts_{args.task}_extended.json'

    # Load tts_prompts.json
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    if args.task == 'counting':
        prompts = extend_counting_task(args.n, prompts)
    else:
        prompts = extend_general_task(args.task, args.n, prompts)

    save_extended(prompts, output_file)
