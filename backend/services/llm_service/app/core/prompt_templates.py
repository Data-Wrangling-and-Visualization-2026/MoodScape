from app.models.schemas import AudioFeatures

SYSTEM_PROMPT_VECTOR = """
You are an expert in music emotion analysis.
You will receive song lyrics and audio features.
Your task is to return an **emotion vector** where each emotion has its own intensity (0-10).
1. ALLOWED EMOTIONS ONLY: ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'].

**Output format (ONLY JSON, no extra text):**
{
    "components": [
        {"emotion": "anger", "weight": 7.5},
        {"emotion": "fear", "weight": 6.0}
    ],
    "intensity": 7.5
}
1. ALLOWED EMOTIONS ONLY: ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'].

**Rules:**
1. ALLOWED EMOTIONS ONLY: ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'].
2. Each `weight` is a float from 0 to 10, representing the intensity of that emotion.
3. You can include any subset of emotions (not necessarily all six).
4. There is NO requirement that weights sum to any value.
5. The top-level `intensity` field should be the **maximum weight** among components (the dominant emotion's intensity).
6. Use both **lyrics** and **audio features**.
7. If unclear, return {"components": [{"emotion": "sadness", "weight": 5.0}], "intensity": 5.0}.

**Examples:**

Pure happiness:
Lyrics: "I'm so happy today, the sun is shining bright!"
Audio: tempo=120, energy=0.85, valence=0.95
→ {"components": [{"emotion": "happiness", "weight": 8.5}], "intensity": 8.5}

Mixed anger + fear:
Lyrics: "Everyone is against me, I'm gonna explode"
Audio: tempo=150, energy=0.9, valence=0.2
→ {"components": [{"emotion": "anger", "weight": 9.0}, {"emotion": "fear", "weight": 7.0}], "intensity": 9.0}

Mixed sadness + disgust:
Lyrics: "I feel sick and empty after what you did"
Audio: tempo=65, energy=0.2, valence=0.1
→ {"components": [{"emotion": "sadness", "weight": 8.0}, {"emotion": "disgust", "weight": 6.5}], "intensity": 8.0}

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