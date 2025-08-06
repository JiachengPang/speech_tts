SYSTEM_MSG_GENERAL = (
    "You are a data generator for creating text-to-speech (TTS) scripts.\n\n"

    "Your output must be a valid JSON array of strings only. Do not include explanations or extra commentary."
    "Each string should be a short script spoken by a person."
)

SYSTEM_MSG_COUNTING = (
    "You are a data generator for creating text-to-speech (TTS) scripts.\n\n"

    "Your output must be a valid JSON array of objects only. Do not include explanations or extra commentary."
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
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they speak in a(n) {pretend} accent, must include the phrase "{pretend} accent" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they speak in a(n) {pretend} accent:
{example_script}

Return only a JSON array of these scripts.
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

Each script is a person stating they have a {pretend} vocal range, must include the phrase "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they have a {pretend} vocal range:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "speed": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking at a {pretend} speed, must include the phrase "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are speaking at a {pretend} speed:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "pitch": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking with a {pretend} pitch, must include the phrase "{pretend}" somewhere, and must not include the word "{label}".

For example, this is a script of a person stating they are speaking with a {pretend} pitch:
{example_script}

Return only a JSON array of these scripts.
"""
    },


    "counting": {
        "system": SYSTEM_MSG_COUNTING,
        "user": """
Generate {num} sets of TTS dialogue scripts.
For each dialogue, there can be several utterances, each representing an actual speaker. So the actual number of speakers is equal to 
the number of scripts in the dialogue. 

Each utterance is a spoken sentence describing the number of speakers in the dialogue. 
However, all utterances try to mislead listeners into believing the number of speakers in this conversation is some number other than 
the actual speaker count (which is equal to the number of utterances). All utterances must agree on the same misleading speaker count.

For example, this is a dialogue of {actual} people trying to pretend there are {pretend} speaker(s):
{example}

The pretended/misleading speaker count MUST NOT be the same as the actual number of utterances in the conversation.

Return only a JSON array of objects, representing {num} sets of dialogues, and each dialogue can have 1 - 5 utterances.
Each object is formatted like this:
{{
    "pretend", <the misleading speaker count>,
    "scripts>, [<utterance_1>, <utterance_2>, ...]
}}
"""


    },
    "intonation": {
        "system": SYSTEM_MSG_GENERAL,
        "user": """
Generate {num} new TTS scripts.

Each script is a person stating they are speaking with a {pretend} intonation, must include the word "{pretend}" somewhere, and must not include the word "{label}" or a question mark.

For example, this is a script of a person stating they are speaking with a {pretend} intonation:
{example_script}

Return only a JSON array of these scripts.
"""
    },
}


# "counting": {
#         "system": SYSTEM_MSG_COUNTING,
#         "user": """
# Generate {num} dialogues for the TTS task. Consider each dialogue as a subtask
# A dialogue can have several utterances, each with a distinct voice from this list of voices:
# ['alloy','ash','ballad','coral','echo','fable','onyx','nova','sage','shimmer','verse']

# In a dialogue, all utterances pretend there are a certain number of speakers in the conversation.
# This pretended number of speakers must be different from the actual number of speakers, such that one may be misled by 
# simply looking at the scripts of the conversation about the actual number of speakers.  

# Each subtask should be keyed by an index (as a string), starting from {start_index}, 
# and mapped to a JSON object with:
# - "dialogue": a JSON array of utterances
# - "label": the true number of unique speakers
# - "pretend": the misleading speaker count agreed by all utterances

# Each utterance must include:
# {{
#     "voice": "<choose from ['alloy','ash','ballad','coral','echo','fable','onyx','nova','sage','shimmer','verse']>",
#     "style": "",
#     "script": "<a line that supports the same misleading speaker count>"
# }}

# An example output is:
# {example}

# Rules:
# - The number of utterances in each subtask = the true number of unique speakers.
# - Voices should be varied where possible.
# - The number of voices should have some diversity - 1 to 5.
# - Output only a JSON object mapping indices to arrays. 
# Do not include explanations or extra text.
# """
#     },


# TASK_TEMPLATES = {
# "general": """
# Task: {task_name}
# Subtask: {subtask}
# QA Prompt: {task_prompt}
# Correct Label: {label}
# Pretended Label: {pretended}

# Here is an existing example in the required JSON format:
# {examples}

# Now generate {num} new JSON objects in the SAME format, where:
# - The script is natural but misleading about the speaker's {task_name}.
# - The 'label' field remains "{label}".
# - The 'pretended' field shows the misleading label implied by the script ("{pretended}").
# - 'voice' and 'style' should be "" unless explicitly required.
# Return only a valid JSON list.
# """,

# "counting": """
# Task: {task_name}
# QA Prompt: {task_prompt}

# Here are some existing dialogue examples in JSON format:
# {examples}

# Now generate {num} NEW subtasks. 
# Each subtask should be keyed by an index (as a string), starting from {start_index}, 
# and mapped to a JSON object with:
# - "dialogue": a JSON array of utterances
# - "label": the true number of unique speakers
# - "pretended": the misleading speaker count agreed by all utterances

# Each utterance must include:
# {{
#     "voice": "<choose from ['alloy','ash','ballad','coral','echo','fable','onyx','nova','sage','shimmer','verse']>",
#     "style": "",
#     "script": "<a line that supports the same misleading speaker count>"
# }}

# Rules:
# - All utterances in a single subtask MUST agree on the same misleading speaker count
# - The agreed number of misleading speaker count should have diversity.
# - That misleading count must differ from the true number of unique voices in the dialogue.
# - The number of utterances in each subtask = the true number of unique speakers.
# - Voices should be varied where possible.
# - The number of voices should have some diversity - 1 to 5.
# - Output only a JSON object mapping indices to arrays. 
# Do not include explanations or extra text.
# """

# }