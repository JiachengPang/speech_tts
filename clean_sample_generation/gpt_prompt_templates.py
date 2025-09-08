SYSTEM_MSG_GENERAL = (
    "You are a data generator for creating text-to-speech (TTS) scripts.\n\n"

    "Your output must be a valid JSON array of strings only. Do not include explanations or extra commentary."
    "Each string should be a short script spoken by a person."
)

SYSTEM_MSG_OBJECT = (
    "You are a data generator for creating text-to-speech (TTS) scripts.\n\n"

    "Your output must be a valid JSON array of objects only. Do not include explanations or extra commentary."
)

SYSTEM_MSG_ARRAY = (
    "You are a data generator for creating text-to-speech (TTS) scripts.\n\n"

    "Your output must be a valid 2D JSON array of strings only. Do not include explanations or extra commentary."
)


# SYSTEM_MSG_COUNTING = (
#     "You are a data generator tasked with creating contrastive prompts for a Text-To-Speech (TTS) "
#     "evaluation dataset. The purpose of this dataset is to test whether models can correctly identify "
#     "speech attributes (such as volume, pitch, speed, emotion, age, gender, intonation, pauses, or accents) "
#     "from the audio signal itself, rather than relying only on the textual content.\n\n"
    
#     "Contrastive means that the STYLE of speech and the SCRIPT content should intentionally conflict. "
#     "For example, a style might say 'Speak in a whisper with very low energy,' while the script might read "
#     "'I'm shouting as loud as I possibly can!' In this way, the text content misleads the listener about the "
#     "true speech attribute.\n\n"
    
#     "Your goal is to produce misleading but realistic TTS prompts that challenge models to rely on the audio, "
#     "not just the text."

#     "Your output must be valid JSON only. Do not include explanations or extra commentary. "
#     "The specific JSON schema will be given in the user prompt depending on the task."
# )

TASK_TEMPLATES = {
    "age": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a {pretend} person stating they are {pretend}, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are {pretend}:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "gender": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a {pretend} person stating they are {pretend}, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are {pretend}:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "accent": {
        "system": SYSTEM_MSG_OBJECT,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they speak in some accent other than "{label}" and must not include the word "{label}".
The script should have at least 20 words, and should contain words or phrases that can easily expose a person's accent.
Do not include any non-English word.
You should also include the accent this speaker is claiming to have in a JSON object like this:
{{
    "script": <your script>,
    "pretend": <the accent the speaker claims to have>
}}

For example, this is an example output JSON array of objects.
{example_object}

Return only a JSON array of these objects.
"""
    },

    
    "volume": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking in a {pretend} voice, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are speaking in a {pretend} voice:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "range": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they have a {pretend} vocal range, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they have a {pretend} vocal range:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "speed": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking at a {pretend} speed, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are speaking at a {pretend} speed:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "pitch": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking with a {pretend} pitch, must include the word "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are speaking with a {pretend} pitch:
{example_script}

Return only a JSON array of these scripts.
"""
    },

    "counting": {
        "system": SYSTEM_MSG_ARRAY,
        "user": """
Generate {num} sets of TTS dialogue scripts.

For each dialogue, there must be {num_utterances} utterance(s).

Return only a JSON array of these dialogues. Each dialogue is a JSON array of utterances. Each utterance is a spoken sentence.

Your response should be a valid 2D JSON array of strings only. Do not include explanations or extra commentary.
"""
    },


    "intonation": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking with a {pretend} intonation, must include the word "{pretend}" somewhere, and must not include the word "{label}".

Your script must NOT include any punctuation.

For example, this is a script of a person stating they are speaking with a {pretend} intonation:
{example_script}

Your scripts should have diversity and should not simply follow the provided example.

Return only a JSON array of these scripts.
"""
    },


    "pause": {
        "system": SYSTEM_MSG_OBJECT,
        "user": """
Generate {num} new TTS scripts.

Your output MUST be a JSON array of objects.
Each object must have:
- "script": a sentence in everyday spoken English where a pause could naturally occur in more than one place.
- "pauses": a list of 2-4 single words in that sentence that could naturally be followed by a pause (MUST NOT be the last word in that sentence).

Your script MUST NOT contain any punctuation.

Example format:
[
  {{
    "script": <your script>,
    "pauses": <your list of words>
  }}
]
"""
    },

    
    "prolong": {
        "system": SYSTEM_MSG_OBJECT,
        "user": """
Generate {num} new TTS scripts.

Your output MUST be a JSON array of objects.
Each object must have:
- "script": a sentence in everyday spoken English where more than one word could naturally be prolonged, to convey different meanings.
- "prolonged": a list of 2-4 words in that sentence that could naturally be prolonged.

Your script MUST NOT contain any punctuation.

Example format:
[
  {{
    "script": <your script>,
    "prolonged": <your list of words>
  }}
]
"""
    },


    "stress": {
        "system": SYSTEM_MSG_OBJECT,
        "user": """
Generate {num} new TTS scripts.

Your output MUST be a JSON array of objects.
Each object must have:
- "script": a sentence in everyday spoken English where more than one word could naturally be stressed, to convey different meanings.
- "stressed": a list of 2 words in that sentence that could naturally be stressed, and it MUST NOT include the last word in that sentence.

Your script MUST NOT contain any punctuation.

Example format:
[
  {{
    "script": <your script>,
    "stressed": <your list of words>
  }}
]
"""
    },


    "identity": {
        "system": SYSTEM_MSG_ARRAY,
        "user": """
Generate {num} sets of TTS dialogue scripts.

For each dialogue, there must be {num_utterances} utterance(s). The utterances must be irrelevant to each other and should not form a coherent conversation.

Return only a JSON array of these dialogues. Each dialogue is a JSON array of utterances. Each utterance is a spoken sentence.

Your response should be a valid 2D JSON array of strings only. Do not include explanations or extra commentary.

"""
    }
}