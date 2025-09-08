#!/bin/bash

N="${1:-50}"

echo "$N"

python gpt_prompt_generation.py --task pause   --n "$N"
python gpt_prompt_generation.py --task prolong --n "$N"
python gpt_prompt_generation.py --task stress  --n "$N"