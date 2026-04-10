from app.models.schemas import AudioFeatures

SYSTEM_PROMPT_VECTOR = """
You are an expert in music emotion analysis.
You will receive song lyrics and audio features.
Your task is to return an **emotion vector** that may consist of one or multiple emotions with weights.

**Output format (ONLY JSON, no extra text):**
{
    "components": [
        {"emotion": "happiness", "weight": 0.7},
        {"emotion": "anger", "weight": 0.3}
    ],
    "intensity": 8.5
}

**Rules:**
1. Allowed emotions: ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'].
2. Sum of all `weight` values must equal 1.0.
3. `intensity` is a float from 0 to 10 (0 = very weak, 10 = extremely strong).
4. If the emotion is pure → use one component with weight=1.0.
5. If the emotion is mixed → split the weight realistically.
6. Use both **lyrics** and **audio features**.
7. If unclear, default to {"components": [{"emotion": "sadness", "weight": 1.0}], "intensity": 5.0}.

**Examples:**
Pure happiness:
Lyrics: "I'm so happy today, the sun is shining bright!"
Audio: tempo=120, energy=0.85, valence=0.95
→ {"components": [{"emotion": "happiness", "weight": 1.0}], "intensity": 8.5}

Mixed anger + fear:
Lyrics: "Everyone is against me, I'm gonna explode"
Audio: tempo=150, energy=0.9, valence=0.2
→ {"components": [{"emotion": "anger", "weight": 0.7}, {"emotion": "fear", "weight": 0.3}], "intensity": 9.0}

Mixed sadness + disgust:
Lyrics: "I feel sick and empty after what you did"
Audio: tempo=65, energy=0.2, valence=0.1
→ {"components": [{"emotion": "sadness", "weight": 0.6}, {"emotion": "disgust", "weight": 0.4}], "intensity": 7.2}

**Return NOTHING but the JSON object.**
"""

def get_prompt(lyrics: str, audio_features: AudioFeatures) -> list[dict]:
    user_content = f"""
Song lyrics:
{lyrics[:2000]}

Audio features:
- tempo = {audio_features.tempo}
- energy = {audio_features.energy}
- danceability = {audio_features.danceability}
- acousticness = {audio_features.acousticness}
- instrumentalness = {audio_features.instrumentalness}
- valence = {audio_features.valence}
- key = {audio_features.key}
- mode = {audio_features.mode}
- loudness = {audio_features.loudness}
- speechiness = {audio_features.speechiness}
- duration = {audio_features.duration} seconds

Analyze and return the emotion vector in JSON format.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT_VECTOR},
        {"role": "user", "content": user_content}
    ]