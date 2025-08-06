import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
load_dotenv()

import os

SPEECH_KEY = os.getenv('AZURE_API_KEY')
SPEECH_REGION = os.getenv('AZURE_API_REGION')

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

def synthesize_ssml_to_file(ssml_file, output_file):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Load SSML text
    with open(ssml_file, 'r', encoding='utf-8') as f:
        ssml_text = f.read()

    result = synthesizer.speak_ssml_async(ssml_text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f'Audio saved to {output_file}')
    else:
        print(f'Error: {result.reason}')
        if result.cancellation_details:
            print('Details:', result.cancellation_details)

ssml_file = 'ssml/test.ssml'
output = 'test_outupt.wav'
synthesize_ssml_to_file(ssml_file, output)

# voices = synthesizer.get_voices_async().get()
# print('Available voices:')

# with open('azure_voices.txt', 'w', encoding='utf-8') as f:
#     for v in voices.voices:
#         f.write(f'Name: {v.name}, ShortName: {v.short_name}, Locale: {v.locale}, Gender: {v.gender}')
#         f.write('\n\n')
