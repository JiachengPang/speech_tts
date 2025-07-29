# Hallucinating Samples Generation Tests
AF3, AF2, SALMONN Responses under each audio. ✅ means answer is likely correct, ❌ means the generated speech is bad.

## Paralinguistic perception tasks

### 1. Volume comparison 
AF3 prompt: Describe the volume of this speech.

#### 1.1. Low volume speech, high volume script 
11Labs: cannot control volume. 

OpenAI: \
Style prompt: Speak in a whisper, low volume, with very low energy. \
Script: I’m literally screaming at the top of my lungs!

<audio controls>
    <source src="samples/openai_volume_1.wav" type="audio/wav">
</audio>

The speech is loud.

low ✅

<audio controls>
    <source src="samples/openai_volume_2.wav" type="audio/wav">
</audio>

The speech is very loud.

low ✅

<audio controls>
    <source src="samples/openai_volume_3.wav" type="audio/wav">
</audio>

The speech is loud.

quiet ✅

<audio controls>
    <source src="samples/openai_volume_4.wav" type="audio/wav">
</audio>

The speech is very loud.

low ✅

<audio controls>
    <source src="samples/openai_volume_5.wav" type="audio/wav">
</audio>

The speech is loud.

low ✅

#### 1.2. High volume speech, low volume script 
OpenAI: \
Style prompt: Yell in a high volume with exaggerated intensity and harsh articulation. \
Script: I need to talk quietly because my roommate is asleep.

<audio controls>
    <source src="samples/openai_volume_6.wav" type="audio/wav">
</audio>

quiet

louder ✅

<audio controls>
    <source src="samples/openai_volume_7.wav" type="audio/wav">
</audio>

quiet

loud ✅

<audio controls>
    <source src="samples/openai_volume_8.wav" type="audio/wav">
</audio>

loudly ✅

noisy ✅

<audio controls>
    <source src="samples/openai_volume_9.wav" type="audio/wav">
</audio>

quietly

loud ✅

<audio controls>
    <source src="samples/openai_volume_10.wav" type="audio/wav">
</audio>

quietly

loud ✅

### 2. Vocal range comparison

MMSU: \
"question": "Which vocal range pattern best matches the audio?", \
"choice_a": "medium-low-high", \
"choice_b": "low-high-medium", \
"choice_c": "high-low-medium", \
"choice_d": "high-medium-low"


Hard to synthesize samples due to lack of token-level control. We can just simply use each one individually.

AF3 prompt: What is the vocal range of the utterance? High, low, or medium.


OpenAI: \
Style prompt: Speak in a low vocal range. \
Script: My vocal range is so high.


<audio controls>
    <source src="samples/openai_vocalrange_1.wav" type="audio/wav">
</audio>

High

high

Style prompt: Speak in a high vocal range. \
Script: My vocal range is so low.

<audio controls>
    <source src="samples/openai_vocalrange_2.wav" type="audio/wav">
</audio>

low

the vocal range of the utterance is high. ✅

Style prompt: Speak in a medium vocal range. \
Script: My vocal range is so high.


<audio controls>
    <source src="samples/openai_vocalrange_3.wav" type="audio/wav">
</audio>

High

high

11Labs: \
No filter for vocal range. Have to manually select voice.

<audio controls>
    <source src="samples/11labs_vocalrange_1.mp3" type="audio/mp3">
</audio>

High

high

<audio controls>
    <source src="samples/11labs_vocalrange_2.mp3" type="audio/mp3">
</audio>

Low

low.

### 3. Speed Comparison

MMSU: \
"question": "Which speed pattern best matches the audio?", \
"choice_a": "medium-low-high", \
"choice_b": "high-low-medium", \
choice_c": "medium-high-low", \
"choice_d": "low-high-medium",

Similar to vocal range, cannot manipulate token level generation, but can use each speech individually.

AF3 prompt: Describe the speed of this speech.

#### 3.1 Fast speech, slow script

OpenAI: \
Style prompt: Speak at a high speed, as quickly as possible, with minimum pause, like a rushed statement under time pressure. \
Script: I always speak as slowly and as clearly as I can.


<audio controls>
    <source src="samples/openai_speed_1.wav" type="audio/wav">
</audio>

slow

fast ✅

<audio controls>
    <source src="samples/openai_speed_2.wav" type="audio/wav">
</audio>

slowly

fast ✅

<audio controls>
    <source src="samples/openai_speed_3.wav" type="audio/wav">
</audio>

slowly

medium ✅

<audio controls>
    <source src="samples/openai_speed_4.wav" type="audio/wav">
</audio>

slowly

fast ✅

<audio controls>
    <source src="samples/openai_speed_5.wav" type="audio/wav">
</audio>

slowly

fast ✅

11Labs: though speed adjustment is provided, the actual effect varies quite a bit with different voices, so still need to manually select voice.


<audio controls>
    <source src="samples/11labs_speed_1.mp3" type="audio/mp3">
</audio>

slowly

fast ✅

<audio controls>
    <source src="samples/11labs_speed_2.mp3" type="audio/mp3">
</audio>

slowly

fast ✅

<audio controls>
    <source src="samples/11labs_speed_3.mp3" type="audio/mp3">
</audio>

Bad generation❌

slowly ✅

fast

#### 3.2 Slow speech, fast script

OpenAI: \
Style prompt: Speak at a very slow speed, as slow as possible, stretching out words and pausing frequently. \
Script: I’m talking super fast right now, keep up with me.



<audio controls>
    <source src="samples/openai_speed_6.wav" type="audio/wav">
</audio>

super fast

fast

<audio controls>
    <source src="samples/openai_speed_7.wav" type="audio/wav">
</audio>

super fast

149.0

<audio controls>
    <source src="samples/openai_speed_8.wav" type="audio/wav">
</audio>

super fast

fast

<audio controls>
    <source src="samples/openai_speed_9.wav" type="audio/wav">
</audio>

fast

fast

<audio controls>
    <source src="samples/openai_speed_10.wav" type="audio/wav">
</audio>

superfast

slower ✅

11Labs:

<audio controls>
    <source src="samples/11labs_speed_4.mp3" type="audio/mp3">
</audio>

superfast

fast

<audio controls>
    <source src="samples/11labs_speed_5.mp3" type="audio/mp3">
</audio>

super fast

fast

<audio controls>
    <source src="samples/11labs_speed_6.mp3" type="audio/mp3">
</audio>

super fast

fast

### 4. Pitch comparison

AF3 prompt: Is the speaker's pitch high or low?

#### 4.1 High pitch speech, low pitch script

OpenAI: \
Style prompt: Speak with very high pitch, bright, slightly squeaky. \
Script: My voice is naturally deep and low.


<audio controls>
    <source src="samples/openai_pitch_1.wav" type="audio/wav">
</audio>

The speaker's pitch is low.

the pitch of the speaker's voice is not indicated in the clip.

<audio controls>
    <source src="samples/openai_pitch_2.wav" type="audio/wav">
</audio>

The speaker's pitch is low.

based on the audio description, the pitch of the speaker is lower.

<audio controls>
    <source src="samples/openai_pitch_3.wav" type="audio/wav">
</audio>

The speaker's pitch is low.

the speaker's pitch is high. ✅

<audio controls>
    <source src="samples/openai_pitch_4.wav" type="audio/wav">
</audio>

The speaker's pitch is low.

the speaker's pitch is not mentioned in the given audio clip.

<audio controls>
    <source src="samples/openai_pitch_5.wav" type="audio/wav">
</audio>

The speaker's pitch is low.

it's hard to tell from the audio alone.

11labs:

<audio controls>
    <source src="samples/11labs_pitch_1.mp3" type="audio/mp3">
</audio>

The speaker's pitch is low.

it is unknown from the given information.

#### 4.2 Low pitch speech, high pitch script

OpenAI: \
Style prompt: Speak with very high pitch, bright, slightly squeaky. \
Script: My voice is naturally deep and low.


<audio controls>
    <source src="samples/openai_pitch_6.wav" type="audio/wav">
</audio>

The speaker's pitch is high.

the audio clip doesn't provide information about the speaker's pitch.

<audio controls>
    <source src="samples/openai_pitch_7.wav" type="audio/wav">
</audio>

The speaker's pitch is high.

the pitch of the speaker is high.

<audio controls>
    <source src="samples/openai_pitch_8.wav" type="audio/wav">
</audio>

The speaker's pitch is high.

the pitch of the speaker is relatively low. ✅

<audio controls>
    <source src="samples/openai_pitch_9.wav" type="audio/wav">
</audio>

The speaker's pitch is high.

unknown, more information is needed.

<audio controls>
    <source src="samples/openai_pitch_10.wav" type="audio/wav">
</audio>

The speaker's pitch is high.

the pitch of the speaker is low. ✅

11labs:

<audio controls>
    <source src="samples/11labs_pitch_2.mp3" type="audio/mp3">
</audio>

The speaker's pitch is high.

the speaker's pitch is deep. ✅

### 5. Emotion

AF3 prompt: What is the speaker's emotion state?


#### 5.1 Sad speech, happy script

OpenAI: \
Style prompt: Speak with very high pitch, bright, slightly squeaky. \
Script: My voice is naturally deep and low.



<audio controls>
    <source src="samples/openai_emotion_1.wav" type="audio/wav">
</audio>

The speaker is feeling happy.

neutral or indifferent

<audio controls>
    <source src="samples/openai_emotion_2.wav" type="audio/wav">
</audio>

The speaker is happy.

the speaker appears to be angry. ✅

<audio controls>
    <source src="samples/openai_emotion_3.wav" type="audio/wav">
</audio>

The speaker is happy.

happy.

<audio controls>
    <source src="samples/openai_emotion_4.wav" type="audio/wav">
</audio>

The speaker is feeling happy.

unknown

<audio controls>
    <source src="samples/openai_emotion_5.wav" type="audio/wav">
</audio>

The speaker is happy.

concerned ✅

#### 5.2 Happy speech, sad script

OpenAI: \
Style prompt: Speak in an extremely happy, cheerful, and energetic tone with an upbeat rhythm and smiling inflection, as if delivering great, exciting news. \
Script: I’ve lost everything I cared about, and I have never been so sad.


<audio controls>
    <source src="samples/openai_emotion_6.wav" type="audio/wav">
</audio>

sad

excited ✅

<audio controls>
    <source src="samples/openai_emotion_7.wav" type="audio/wav">
</audio>

The speaker is expressing sadness.

the audio clip suggests that the speaker is feeling anxious or fearful.

<audio controls>
    <source src="samples/openai_emotion_8.wav" type="audio/wav">
</audio>

angry ✅

there is insufficient information to determine the speaker's emotion state.

<audio controls>
    <source src="samples/openai_emotion_9.wav" type="audio/wav">
</audio>

angry ✅

unknown, not mentioned in the audio clip.

<audio controls>
    <source src="samples/openai_emotion_10.wav" type="audio/wav">
</audio>

sad

unknown

### 6. Total speaker counting

Maybe piece together multiple synthesized speech?

AF3 prompt: How many different speakers are in the audio?

11labs:

<audio controls>
    <source src="samples/11labs_speakercount_3.mp3" type="audio/mp3">
</audio>

There are three different speakers in the audio.

there are multiple speakers in the audio.

### 7. Age prediction

Hard to control age with OpenAI. More easy to find young voice actors on 11Labs

AF3 prompt: What is the most likely age group of the speaker in the audio?

11Labs:

<audio controls>
    <source src="samples/11labs_age_1.mp3" type="audio/mp3">
</audio>

The speaker is most likely an elderly person, turning 83 this year.

the most likely age group of the speaker in the audio is a pre-school child. ✅

<audio controls>
    <source src="samples/11labs_age_2.mp3" type="audio/mp3">
</audio>

The speaker is most likely a young child.

the speaker is an adult. ✅

### 8. Gender prediction

AF3 prompt: What is the speaker's gender?

#### 8.1 Female speech, male script

OpenAI: \
Style prompt: Speak in a female voice. \
Script: I am a grown man and I know what to do.

<audio controls>
    <source src="samples/openai_gender_1.wav" type="audio/wav">
</audio>

The speaker is female. ✅

the speaker is female. ✅

<audio controls>
    <source src="samples/openai_gender_2.wav" type="audio/wav">
</audio>

male

the speaker is male.

<audio controls>
    <source src="samples/openai_gender_3.wav" type="audio/wav">
</audio>

female ✅

the speaker is female. ✅

<audio controls>
    <source src="samples/openai_gender_4.wav" type="audio/wav">
</audio>

female ✅

the speaker is female.

<audio controls>
    <source src="samples/openai_gender_5.wav" type="audio/wav">
</audio>

The speaker is female. ✅

the speaker is female. ✅

11Labs:

<audio controls>
    <source src="samples/11labs_gender_1.mp3" type="audio/mp3">
</audio>

The speaker is a young boy.

the gender of the speaker is female. ✅

#### 8.2 Male speech, female script

OpenAI: \
Style prompt: Speak in a male voice. \
Script: As a woman, I know these times can be challenging.


<audio controls>
    <source src="samples/openai_gender_6.wav" type="audio/wav">
</audio>

The speaker is male. ✅

the speaker is female.

<audio controls>
    <source src="samples/openai_gender_7.wav" type="audio/wav">
</audio>

The speaker is a woman.

male. ✅

<audio controls>
    <source src="samples/openai_gender_8.wav" type="audio/wav">
</audio>

The speaker is a woman.

male. ✅

<audio controls>
    <source src="samples/openai_gender_9.wav" type="audio/wav">
</audio>

The speaker is a woman.

the speaker's gender is male. ✅

<audio controls>
    <source src="samples/openai_gender_10.wav" type="audio/wav">
</audio>

The speaker is a woman.

the speaker is male. ✅

### 9. Intonation perception

MMSU:
"question": "What is the intonation of the entire sentence in the audio?", \
"choice_a": "Rise-Fall Intonation", \
"choice_b": "Fall-Rise Intonation", \
"choice_c": "Failing Intonation", \
"choice_d": "Rising Intonation"

AF3 prompt: Is the intonation of the entire sentence rising or falling?

#### 9.1 Rising speech, falling script

OpenAI: \
Style prompt: Speak the sentence in a rising intonation, ending with an upward inflection, as if unsure or questioning. \
Script: I am sure my decision is the right choice.



<audio controls>
    <source src="samples/openai_intonation_1.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is falling.

the audio does not allow us to conclude whether the entire sentence is rising or falling in intonation.

<audio controls>
    <source src="samples/openai_intonation_2.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is rising. ✅

based on the sound events, the intonation rises at the beginning and end of the phrase, and falls in the middle. ✅

<audio controls>
    <source src="samples/openai_intonation_3.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is rising. ✅

unknown.

<audio controls>
    <source src="samples/openai_intonation_4.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is rising. ✅

we need more information about the specific sentence to determine the intonation.

<audio controls>
    <source src="samples/openai_intonation_5.wav" type="audio/wav">
</audio>

Bad generation ❌

The intonation of the entire sentence is falling. ✅

the information provided in the audio clip is not sufficient to determine whether the intonation of the entire sentence is rising or falling.

#### 9.2 Falling speech, rising script

OpenAI: \
Style prompt: Speak the sentence in a falling intonation, ending with a downward inflection, as if making an assertion rather than asking a question. \
Script: You really think this is a good idea.

Generation quality can be bad.

<audio controls>
    <source src="samples/openai_intonation_6.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is falling. ✅

the entire sentence in the audio clip does not contain any inflection or changes in pitch.

<audio controls>
    <source src="samples/openai_intonation_7.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is falling. ✅

the intonation in this sentence rises.

<audio controls>
    <source src="samples/openai_intonation_8.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is rising.

the intonation of the entire sentence falls. ✅

<audio controls>
    <source src="samples/openai_intonation_9.wav" type="audio/wav">
</audio>

The intonation of the entire sentence is falling. ✅

the audio content suggests that the intonation of the entire sentence is falling. ✅

<audio controls>
    <source src="samples/openai_intonation_10.wav" type="audio/wav">
</audio>

Bad generation ❌

The intonation of the entire sentence is rising. ✅

the intonation of the entire sentence falls.

### 10. Pause perception

AF3 prompt: Which word is most likely followed by a pause in the audio?

OpenAI: \
Style prompt: Speak fluently with absolutely no pause, and only add a pause where you see the [pause] token. \
Script: Of course I [pause] believe what you said.

Hard to generate good speech samples.


<audio controls>
    <source src="samples/openai_pause_1.wav" type="audio/wav">
</audio>

The word 'believe' is most likely followed by a pause in the audio.

'end'

<audio controls>
    <source src="samples/openai_pause_2.wav" type="audio/wav">
</audio>

Bad generation ❌ \
The word 'pause' is most likely followed by a pause in the audio.

b.

<audio controls>
    <source src="samples/openai_pause_3.wav" type="audio/wav">
</audio>

Bad generation ❌ \
The word 'believe' is most likely followed by a pause in the audio.

a

<audio controls>
    <source src="samples/openai_pause_4.wav" type="audio/wav">
</audio>

Bad generation ❌ \
The word 'believe' is most likely followed by a pause in the audio.

none

<audio controls>
    <source src="samples/openai_pause_5.wav" type="audio/wav">
</audio>

Bad generation ❌ \
The word 'believe' is most likely followed by a pause in the audio.

santa claus

### 11. Prolonged sound perception

AF3 prompt: Which word contains noticeable elongation in the audio?

OpenAI: \
Style prompt: Speak fluently in a fast pace, but significantly prolong the word "talking". \
Script: I know exactly what I am talking about.

Tricky to generate good speech samples.

<audio controls>
    <source src="samples/openai_prolonged_1.wav" type="audio/wav">
</audio>

The word 'exactly' contains noticeable elongation in the audio.

the word 'very' contains noticeable elongation in the audio.

<audio controls>
    <source src="samples/openai_prolonged_2.wav" type="audio/wav">
</audio>

Bad generation ❌ \
The word 'exactly' contains noticeable elongation in the audio.

the word 'digital' contains noticeable elongation in the audio.

<audio controls>
    <source src="samples/openai_prolonged_3.wav" type="audio/wav">
</audio>

The word 'know' contains noticeable elongation in the audio.

the word 'ten' contains noticeable elongation in the audio.

<audio controls>
    <source src="samples/openai_prolonged_4.wav" type="audio/wav">
</audio>

exactly

the word containing noticeable elongation in the audio is 'long'.

<audio controls>
    <source src="samples/openai_prolonged_5.wav" type="audio/wav">
</audio>

The word 'exactly' contains noticeable elongation in the audio.

the word 'funk' contains noticeable elongation in the audio.

### 12. Accent identification

AF3 prompt: What accent does the speaker's voice most likely correspond to?

Tricky to generate with style prompt, 11Labs has more voice to choose from.

11labs:


<audio controls>
    <source src="samples/11labs_accent_1.mp3" type="audio/mp3">
</audio>

The speaker's voice most likely corresponds to a Chinese accent.

the accent of the speaker's voice is not known.



## Skipped: 
1. Speaker identityrecognition
2. Speech stressperception
3. Syllable perception
4. Plosive soundidentification
5. Consonant & vowel perception
6. Near-homophoneperception
7. All semantics perception tasks (ASR)

