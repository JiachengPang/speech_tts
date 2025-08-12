import argparse
import json
import os

from string import punctuation

import random
random.seed(42)

TASK_NAME_MAP = {
    'accent': 'accent_identification',
    'age': 'age_prediction',
    'counting': 'total_speaker_counting',
    'gender': 'gender_prediction',
    'intonation': 'intonation_perception',
    'pause': 'pause_perception',
    'prolong': 'prolonged_sound_perception',
    'stress': 'speech_stress_perception',
    'volume': 'volume_comparison',
    'pitch': 'pitch_comparison',
    'speed': 'speed_comparison',
    'range': 'vocal_range_comparison'
}

def load_and_join(input_path, delimiter='|'):
    keys = ('task', 'subtask', 'index', 'voice')
    data = {}

    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception as e:
                print(f'Failed to parse line {i}: {e}')
                continue
            
            for field, value in list(obj.items()):
                if isinstance(value, list):
                    obj[field] = delimiter.join(str(x) for x in value)

            try:
                key = tuple(obj[k] for k in keys)
            except KeyError as e:
                print(f"Missing key {e} at line {i}")
                continue

            data[key] = (obj, i)

    ordered = [obj for obj, _ in sorted(data.values(), key= lambda x: x[1])]
    print(f'loaded {len(ordered)} examples after deduplication.')

    return ordered

def verify_file_integrity(data, data_dir='./tts_outputs'):
    task_sample_count = {}
    missing = []
    for item in data:
        path = item.get('path')
        path = os.path.join(data_dir, path)
        if not path or os.path.isfile(path):
            missing.append(item)
        else:
            task = item['task']
            if task not in task_sample_count:
                task_sample_count[task] = 1
            else:
                task_sample_count[task] += 1
                

    total = len(data)
    missing_count = len(missing)
    print(f"Checked {total} files: {total - missing_count} found, {missing_count} missing")

    return missing, task_sample_count

def make_random_choices(all_options, answer_gt, pretend_label, n_choices=4):
    pool = set(all_options)
    pool.add(answer_gt)
    pool.add(pretend_label)

    selected = {answer_gt, pretend_label}

    rest = list(pool - selected)
    random.shuffle(rest)
    selected.update(rest[:max(0, n_choices - len(selected))])

    selected = list(selected)
    random.shuffle(selected)

    return selected

def make_mcq(question, options, answer, pretend):
    q = {'question': question}
    o = (options + [None] * 4)[:4]
    letters = ['a', 'b', 'c', 'd']
    choices = {f'choice_{letters[i]}': o[i] for i in range(4)}
    answer_gt = {'answer_gt': answer}
    pretend_label = {'pretend_label': pretend}

    return q | choices | answer_gt | pretend_label

def mcq_age(entry):
    options = ['Elderly adult', 'Child', 'Young adult', 'Middle-aged adult']
    gt_map = {'young': 'Young adult', 'old': 'Elderly adult'}
    
    question = 'What is the most likely age group of the speaker in the audio?'
    answer = gt_map[entry['label']]
    pretend = gt_map[entry['pretend']]

    return make_mcq(question, options, answer, pretend)

def mcq_gender(entry):
    options = ['Female', 'Male']
    
    question = "What is the speaker's gender?"
    answer = entry['label']
    pretend = entry['pretend']

    return make_mcq(question, options, answer, pretend)

def mcq_intonation(entry):
    options = ['Rise-fall intonation', 'Fall-rise intonation', 'Falling intonation', 'Rising intonation']
    gt_map = {'rising': 'Rising intonation', 'falling': 'Falling intonation', 'Rise-fall': 'Rise-fall intonation', 'Fall-rise': 'Fall-rise intonation'}
    
    question = 'What is the intonation of the entire sentence in the audio?'
    answer = gt_map[entry['label']]
    pretend = gt_map[entry['pretend']]

    return make_mcq(question, options, answer, pretend)

def mcq_counting(entry):
    all_options = list(range(1, 11))
    all_options = [f'{n} people' for n in all_options]
    
    question = 'How many different speakers are in the audio?'
    answer = f"{entry['label']} people"
    pretend = f"{entry['pretend']} people"

    options = make_random_choices(all_options, answer, pretend)

    return make_mcq(question, options, answer, pretend)

def mcq_pause(entry):
    script = entry['script']
    sentence = script.split(', and')[1].strip(punctuation)
    all_options = sentence.split(' ')
    all_options.append('No pause')
    
    question = "Which word is most likely followed by a pause in the audio? If there is no pause, select 'No pause'."

    answer = entry['label']
    pretend = entry['pretend']

    options = make_random_choices(all_options, answer, pretend)

    return make_mcq(question, options, answer, pretend)

def mcq_prolong(entry):
    script = entry['script']
    sentence = script.split(', and')[1].strip(punctuation)
    all_options = sentence.split(' ')
    
    question = "Which word contains noticeable elongation in the audio?"

    answer = entry['label']
    pretend = entry['pretend']

    options = make_random_choices(all_options, answer, pretend)

    return make_mcq(question, options, answer, pretend)

def mcq_stress(entry):
    script = entry['script']
    sentence = script.split(', and')[1].strip(punctuation)
    all_options = sentence.split(' ')
    
    question = "Which word has prominent stress in the audio?"

    answer = entry['label']
    pretend = entry['pretend']

    options = make_random_choices(all_options, answer, pretend)

    return make_mcq(question, options, answer, pretend)

def mcq_accent(entry):
    all_options = ['United States', 'United Kingdom', 'Mexico', 'China', 'India', 'Australia', 'France', 'Japan', 'Russia', 'Germany']
    
    gt_map = {'american': 'United States', 'british': 'United Kingdom', 'australian': 'Australia', 'chinese': 'China', 'indian': 'India'}
    
    question = "What accent does the speaker's voice most likely correspond to?"
    answer = gt_map[entry['label']]
    pretend = gt_map[entry['pretend']]

    options = make_random_choices(all_options, answer, pretend)

    return make_mcq(question, options, answer, pretend)

def create_mcqs(data):
    res = []
    for d in data:
        task = d['task']
        task_name = TASK_NAME_MAP[task]
        file_name = d['filename']
        id = f'{task_name}__{file_name}'
        audio_path = f'/audio/{id}.wav'
        if task == 'age':
            mcq = mcq_age(d)
        elif task == 'gender':
            mcq = mcq_gender(d)
        elif task == 'accent':
            mcq = mcq_accent(d)
        elif task == 'intonation':
            mcq = mcq_intonation(d)
        elif task == 'counting':
            mcq = mcq_counting(d)
        elif task == 'pause':
            mcq = mcq_pause(d)
        elif task == 'prolong':
            mcq = mcq_prolong(d)
        elif task == 'stress':
            mcq = mcq_stress(d)
        else:
            continue
        
        example = {
            'id': id,
            'task_name': task_name,
            'audio_path': audio_path,
        } | mcq
        res.append(example)
    
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate JSONL by (task, subtask, index), keeping the last occurrence.")
    parser.add_argument("--input", default="tts_log.jsonl", help="Path to input .jsonl")
    parser.add_argument("--output", default="output_mcq.jsonl", help="Path to write deduped .jsonl")
    args = parser.parse_args()

    # load and deduplicate 
    data = load_and_join(args.input)
    missing, task_sample_count = verify_file_integrity(data)

    if missing:
        print('missing files:')
        for m in missing:
            print(m['path'])
    
    for task in task_sample_count:
        print(f'task {task} has {task_sample_count[task]} samples')

    data = create_mcqs(data)
    data = sorted(
        data,
        key=lambda d: (
            d.get("task", ""),
            d.get("subtask", ""),
            int(d.get("index", 0)),
            d.get("voice", "")
        )
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        for d in data:
            line = json.dumps(d) + '\n'
            f.write(line)