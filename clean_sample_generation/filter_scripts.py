import json

def deduplicate_scripts(prompts, task_name):
    """Remove duplicate examples by script field within each subtask of the given task."""
    task_data = prompts.get(task_name, {})
    for subtask, examples in task_data.items():
        if subtask == "prompt":
            continue
        seen = set()
        unique_examples = []
        for ex in examples:
            script = ex["script"].strip()
            if script not in seen:
                seen.add(script)
                unique_examples.append(ex)
        num_removed = len(examples) - len(unique_examples)
        if num_removed > 0:
            print(f"Removed {num_removed} duplicate scripts from {task_name}/{subtask}")
        task_data[subtask] = unique_examples
    return prompts

# def deduplicate_scripts2(prompts, task_name):
#     """Remove duplicate examples by script field within each subtask of the given task."""
#     task_data = prompts.get(task_name, {})

#     seen = set()
#     unique_examples = {'prompt;': task_data.get('prompt', '')}
#     for idx, substask, example in enumerate(task_data.items()):
#         if substask == "prompt":
#             continue
        
#         print(example)
#         script = example['script'].strip()
#         if script not in seen:
#             seen.add(script)
#             unique_examples[substask] = example
#     num_removed = len(task_data) - len(unique_examples)
#     if num_removed > 0:
#         print(f"Removed {num_removed} duplicate scripts from {task_name}")
#     task_data = unique_examples
#     return prompts

with open("tts_prompts_base_clean.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

prompts = deduplicate_scripts(prompts, task_name="pause")

with open("tts_prompts_base_clean.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, indent=4)
