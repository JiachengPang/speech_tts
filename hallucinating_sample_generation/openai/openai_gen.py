from openai import OpenAI
import argparse

# client = OpenAI()
# speech_file_path = Path(__file__).parent / "speech2.wav"

# with client.audio.speech.with_streaming_response.create(
#     model="gpt-4o-mini-tts",
#     voice="alloy",
#     input="Today is a wonderful day to build something people love!",
#     instructions="Speak in a cheerful and positive tone.",
# ) as response:
#     response.stream_to_file(speech_file_path)

TASKS = ['volume', 'range', 'speed', 'pitch', 'emotion', 'count', 'intonation', 'pause', 'prolong', 'identity', 'stress']
OPENAI_VOICES = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'nova', 'onyx', 'sage', 'shimmer']

def volume_samples(output_dir):
    

    pass

if __name__ == '__main__':
    # need to export OPENAI_API_KEY
    client = OpenAI()
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, required=True, default='volume', choices=TASKS, help='the name of the generation task.')
    parser.add_argument('--output', type=str, required=False, default='./', help='the output dir')

    args = parser.parse_args()
    print(f'args: {args}')

    if args.task == 'volume':
        volume_samples(args.output)
    else:
        raise NotImplementedError("This task is not implemented yet.")