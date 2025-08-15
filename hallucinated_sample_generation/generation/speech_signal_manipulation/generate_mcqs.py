import os
import json
import random
from speech_proc_utils import PitchVariationProcessor, SpeedVariationProcessor, VolumeVariationProcessor, VocalRangeVariationProcessor
from tqdm import tqdm
import logging
from multiprocessing import Pool, cpu_count

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


HIGH_LOW_TASK_COMBINATIONS = ["high-low-medium", "high-medium-low", "low-high-medium", "low-medium-high", "medium-high-low", "medium-low-high"]

def pick_random_subtask_combination(task, correct_subtask):
    if task in ["pitch", "volume", "speed", "vocal_range"]:
        ## first subtask in the combination should not be the correct subtask
        random.shuffle(HIGH_LOW_TASK_COMBINATIONS)
        for combination in HIGH_LOW_TASK_COMBINATIONS:
            if combination.split("-")[0] != correct_subtask:
                return combination
    else:
        raise ValueError(f"Invalid task for picking random subtask combination: {task}")

def generate_mcq_options(task, correct_subtask, correct_choice):
    if task in ["pitch", "volume", "speed", "vocal_range"]:
        ## chose the two options which start with the correct subtask
        options = [opt for opt in HIGH_LOW_TASK_COMBINATIONS if opt.split("-")[0] == correct_subtask]
        options.append(correct_choice)
        random.shuffle(HIGH_LOW_TASK_COMBINATIONS)
        remaining_options = [opt for opt in HIGH_LOW_TASK_COMBINATIONS if opt not in options]
        options.append(remaining_options[0])
        random.shuffle(options)
        return options
    else:
        raise ValueError(f"Invalid task for generating mcq options: {task}")

def format_mcq_mmsu(audio_path, question, options, correct_choice, task_name):
    return_dict = {
        "id": audio_path.split("/")[-1].split(".")[0],
        "audio_path": audio_path,
        "task_name": task_name,
        "question": question,
        "answer_gt": correct_choice
    }
    ### create a,b,c,d options with keys choice_a, choice_b, choice_c, choice_d
    for i, option in enumerate(options):
        return_dict[f"choice_{chr(97 + i)}"] = option
    return return_dict

def generate_one_mcq(item, processor):
    if item["task"] in ["pitch", "volume", "speed", "vocal_range"]:
        cur_style_order = pick_random_subtask_combination(item["task"], item["subtask"])
        test_audio_path = processor.concatenate_audio_three_style(item["path"], style_order = cur_style_order)
        options = generate_mcq_options(item["task"], item["subtask"], cur_style_order)
        return_dict = format_mcq_mmsu(test_audio_path, item["prompt"], options, cur_style_order, item["task"])
        return_dict["pretend_label"] = item["subtask"]
        return return_dict
    else:
        raise ValueError(f"Invalid task for generating mcq: {item['task']}")
        
def get_task_processor(task, parent_save_dir):
    if task == "volume":
        return VolumeVariationProcessor(parent_save_dir)
    elif task == "pitch":
        return PitchVariationProcessor(parent_save_dir)
    elif task == "speed":
        return SpeedVariationProcessor(parent_save_dir)
    elif task == "vocal_range":
        return VocalRangeVariationProcessor(parent_save_dir)
    else:
        raise ValueError(f"Invalid task for getting task processor: {task}")

def _generate_one_and_save(args):
    item_idx, item, processor, task_save_dir = args
    one_mcq_save_path = os.path.join(task_save_dir, "mcqs_temp", f"{item_idx}.json")
    os.makedirs(os.path.dirname(one_mcq_save_path), exist_ok=True)
    
    if os.path.exists(one_mcq_save_path):
        with open(one_mcq_save_path, "r") as f:
            return json.load(f)
    
    one_mcq = generate_one_mcq(item=item, processor=processor)
    with open(one_mcq_save_path, "w") as f:
        json.dump(one_mcq, f, indent=4)
    return one_mcq


def generate_mcqs(jsonl_data, target_task, parent_save_dir, num_workers=24):
    task_save_dir = os.path.join(parent_save_dir, target_task)
    processor = get_task_processor(target_task, parent_save_dir=task_save_dir)
    saved_mcqs = []
    task_items = []

    logging.info(f"Generating mcqs for {target_task}")
    for item_idx, item in enumerate(jsonl_data):
        if item["task"] != target_task:
            continue
        task_items.append((item_idx, item))

    if target_task == "vocal_range":
        logging.info(f"Running in parallel with {num_workers} workers...")
        args = [(item_idx, item, processor, task_save_dir) for item_idx, item in task_items]
        with Pool(processes=num_workers) as pool:
            for mcq in tqdm(pool.imap_unordered(_generate_one_and_save, args), total=len(args)):
                saved_mcqs.append(mcq)
    else:
        for item_idx, item in tqdm(task_items, desc=f"Generating mcqs for {target_task}"):
            one_mcq_save_path = os.path.join(task_save_dir, "mcqs_temp", f"{item_idx}.json")
            os.makedirs(os.path.dirname(one_mcq_save_path), exist_ok=True)
            if os.path.exists(one_mcq_save_path):
                with open(one_mcq_save_path, "r") as f:
                    one_mcq = json.load(f)
                saved_mcqs.append(one_mcq)
                continue
            one_mcq = generate_one_mcq(item=item, processor=processor)
            with open(one_mcq_save_path, "w") as f:
                json.dump(one_mcq, f, indent=4)
            saved_mcqs.append(one_mcq)

    return saved_mcqs

if __name__ == "__main__":
    saved_jsonl_path = "tts_log_signal.jsonl"
    ## read jsonl file
    jsonl_data = []
    with open(saved_jsonl_path, "r") as f:
        for line in f:
            jsonl_data.append(json.loads(line))

    target_tasks = ["vocal_range", "pitch", "volume", "speed"]

    questions = {
        "speed": "Which speed pattern best matches the audio?",
        "volume": "Which volume pattern best matches the audio?",
        "pitch": "Which pitch pattern best matches the audio?",
        "vocal_range": "Which vocal range pattern best matches the audio?"
    }

    benchmark_save_path = "vox_paradox_mcq_signal.json"
    all_save_mcqs = []
    for task in target_tasks:
        saved_mcqs = generate_mcqs(jsonl_data, target_task = task, parent_save_dir = "vox_paradox_mcq_signal")
        all_save_mcqs.extend(saved_mcqs)

    ## fix the questions for all the mcqs
    for mcq in all_save_mcqs:
        mcq["question"] = questions[mcq["task_name"]]

    json.dump(all_save_mcqs, open(benchmark_save_path, "w"), indent=4)
    print(f"Saved {len(all_save_mcqs)} mcqs to {benchmark_save_path}")