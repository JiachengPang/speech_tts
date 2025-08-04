SYSTEM_MSG = (
    "You are a data generator tasked with creating contrastive prompts for a Text-To-Speech (TTS) "
    "evaluation dataset. The purpose of this dataset is to test whether models can correctly identify "
    "speech attributes (such as volume, pitch, speed, emotion, age, gender, intonation, pauses, or accents) "
    "from the audio signal itself, rather than relying only on the textual content.\n\n"
    
    "Contrastive means that the STYLE of speech and the SCRIPT content should intentionally conflict. "
    "For example, a style might say 'Speak in a whisper with very low energy,' while the script might read "
    "'I'm shouting as loud as I possibly can!' In this way, the text content misleads the listener about the "
    "true speech attribute.\n\n"
    
    "Your goal is to produce misleading but realistic TTS prompts that challenge models to rely on the audio, "
    "not just the text."

    "Your output must be valid JSON only. Do not include explanations or extra commentary. "
    "The specific JSON schema will be given in the user prompt depending on the task."
)


TASK_TEMPLATES = {
"general": """
Task: {task_name}
Subtask: {subtask}
QA Prompt: {task_prompt}
Correct Label: {label}
Pretended Label: {pretended}

Here is an existing example in the required JSON format:
{examples}

Now generate {num} new JSON objects in the SAME format, where:
- The script is natural but misleading about the speaker's {task_name}.
- The 'label' field remains "{label}".
- The 'pretended' field shows the misleading label implied by the script ("{pretended}").
- 'voice' and 'style' should be "" unless explicitly required.
Return only a valid JSON list.
""",

"counting": """
Task: {task_name}
QA Prompt: {task_prompt}

Here are some existing dialogue examples in JSON format:
{examples}

Now generate {num} NEW subtasks. 
Each subtask should be keyed by an index (as a string), starting from {start_index}, 
and mapped to a JSON object with:
- "dialogue": a JSON array of utterances
- "label": the true number of unique speakers
- "pretended": the misleading speaker count agreed by all utterances

Each utterance must include:
{{
    "voice": "<choose from ['alloy','ash','ballad','coral','echo','fable','onyx','nova','sage','shimmer','verse']>",
    "style": "",
    "script": "<a line that supports the same misleading speaker count>"
}}

Rules:
- All utterances in a single subtask MUST agree on the same misleading speaker count
- The agreed number of misleading speaker count should have diversity.
- That misleading count must differ from the true number of unique voices in the dialogue.
- The number of utterances in each subtask = the true number of unique speakers.
- Voices should be varied where possible.
- The number of voices should have some diversity - 1 to 5.
- Output only a JSON object mapping indices to arrays. 
Do not include explanations or extra text.
"""

}