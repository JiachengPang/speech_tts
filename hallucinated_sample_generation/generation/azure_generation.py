import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
load_dotenv()

import os

SPEECH_KEY = os.getenv('AZURE_API_KEY')
SPEECH_REGION = os.getenv('AZURE_API_REGION')

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
azure_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

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
output = 'test_output14.wav'
synthesize_ssml_to_file(ssml_file, output)

# def query_azure(ssml: str, output_path: str) -> bool:
#     retries = 0
#     while retries < 5:
#         try:
#             result = azure_synthesizer.speak_ssml_async(ssml).get()

#             if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#                 with open(output_path, "wb") as f:
#                     f.write(result.audio_data)
#                 return True

#             print(f"Err: {result.reason}")
#             if hasattr(result, "cancellation_details") and result.cancellation_details:
#                 print("Details:", result.cancellation_details)
#                 if getattr(result.cancellation_details, "error_details", None):
#                     print("Error details:", result.cancellation_details.error_details)

#         except Exception as e:
#             print(f"Exception during synthesis: {e}")
        
#         retries += 1

#     print(f"Gave up after 5 retries for {output_path}")
#     return False

# ssml = """<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-us">
# <voice name="en-US-GuyNeural">
#         You have such a <prosody rate="-100.00%">nice</prosody> jacket that I want to <break time="1000ms"/> take a photo with you. 
# </voice></speak>"""

# query_azure(ssml, "ssml_test_output.wav")


# def get_azure_voices(n):
#     """Get all Azure English voices."""
#     voices = azure_synthesizer.get_voices_async().get()
#     en_voices = [v for v in voices.voices if v.locale.lower().startswith('en-')]
#     with open('azure_voices_en.txt', 'w', encoding='utf-8') as f:
#         for v in en_voices:
#             f.write(f'Name: {v.name}, ShortName: {v.short_name}, Locale: {v.locale}, Gender: {v.gender}\n')

#     return en_voices

# get_azure_voices(1)

# voices = synthesizer.get_voices_async().get()
# print('Available voices:')

# with open('azure_voices.txt', 'w', encoding='utf-8') as f:
#     for v in voices.voices:
#         f.write(f'Name: {v.name}, ShortName: {v.short_name}, Locale: {v.locale}, Gender: {v.gender}')
#         f.write('\n\n')
