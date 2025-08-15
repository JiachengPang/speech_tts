import argparse
import json


def eval_results(mcq, results):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str)
    parser.add_argument('--test', type=int)
    parser.add_argument('--mcq', type=str, default='vox_paradox_mcq_tts.json')

    args = parser.parse_args()

    print(f'evaluating model {args.model}, test run {args.test}')

    result_path = f'{args.model}/test_outputs{str(args.test)}'
    with open(result_path, 'r', encoding='utf-8') as f:
        results = [json.loads(line) for line in f if line.strip()]

    with open(args.mcq, "r", encoding="utf-8") as f:
        mcqs = json.load(f)

    eval_results(mcqs, results)