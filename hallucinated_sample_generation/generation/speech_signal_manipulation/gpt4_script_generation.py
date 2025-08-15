import os
import json
import argparse
from openai import OpenAI
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

INPUT_FILE = 'tts_prompts_signal.json'

def query(user_msg):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'user', 'content': user_msg},
        ],
        temperature=0.9
    )

    message = response.choices[0].message.content.strip()
    return message

def generate_script_variations(sentence, num_variations):
    prompt = f"""
Your task is to generate multiple variations of a given sentence which mean exactly the same thing. 
Return your response as a JSON array of strings.
Return at least {num_variations} variations.
Following is the sentence to generate variations for: {sentence}
"""

    ans = query(prompt)
    variations = json.loads(ans.lstrip('```json').rstrip('```'))
    logging.info(f"Generated {len(variations)}/{num_variations} variations for {sentence}. {num_variations - len(variations)} variations were not generated.")
    random.shuffle(variations)

    variations_sampled = variations[:20]
    print(f"Sampled variations from the generated {len(variations)} variations: {variations_sampled}")
    return variations
    

def generate_script_variations_for_task_dict(task_dict, num_target, num_speakers=11):
    num_sub_tasks = len(task_dict) - 1
    num_per_subtask = num_target // num_sub_tasks
    logging.info(f"Generating {num_per_subtask} variations per subtask")
    new_task_dict = {}
    for subtask in task_dict:
        if subtask == "prompt":
            continue
        cur_subtask_dict = task_dict[subtask]
        new_cur_subtask_dict = []
        num_cur_scripts = len(cur_subtask_dict)
        num_variations_per_script = num_per_subtask // (num_cur_scripts * num_speakers)
        logging.info(f"Generating {num_variations_per_script} variations per script")
        for cur_script in cur_subtask_dict:
            script_text = cur_script["script"]
            new_cur_subtask_dict.append(cur_script)
            variations = generate_script_variations(script_text, num_variations_per_script)
            for variation in variations:
                new_script = cur_script.copy()
                new_script["script"] = variation
                new_cur_subtask_dict.append(new_script)
        new_task_dict[subtask] = new_cur_subtask_dict
    return new_task_dict

if __name__ == "__main__":
    json_data = json.load(open(INPUT_FILE))
    target_tasks = ["volume", "pitch", "speed", "vocal_range"]
    target_num = 2000

    for target_task in target_tasks:
        task_dict = generate_script_variations_for_task_dict(json_data[target_task], target_num)
        json_data[target_task] = task_dict
    json.dump(json_data, open(f"{INPUT_FILE.split('.')[0]}_gpt4_script_variations.json", "w"), indent=4)
