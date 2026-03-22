from app.models.schemas import AudioFeatures


system = {
        "role": "system", 
        "content": 
        "You are an expert in music emotion analysis."
        "You will get song lyrics and audio features to extract the song primary emotion and emotion intensity."
        "\nRules:"
        "1) RETURN ONLY VALID JSON."
        "2) Allowed emotions: ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']."
        "3) DO NOT use 'neutral', 'calm', or any other emotion outside the list."
        "4) If unclear, use 'sadness' as default."
        "5) emotion_intensity: float from 0 to 10 (0 = very weak, 10 = extremely strong)."
        "\nExamples with audio features:"
        '''
        Lyrics: "I'm so happy today, the sun is shining bright!"
        Audio: tempo=120, energy=0.85, danceability=0.9, valence=0.95
        → {"emotion": "happiness", "emotion_intensity": 8.5}
        
        Lyrics: "My heart is broken, I can't stop crying"
        Audio: tempo=70, energy=0.25, danceability=0.3, valence=0.15
        → {"emotion": "sadness", "emotion_intensity": 9.0}
        
        Lyrics: "I will destroy everyone who stands in my way"
        Audio: tempo=160, energy=0.95, danceability=0.6, valence=0.2, loudness=-5
        → {"emotion": "anger", "emotion_intensity": 9.2}
        
        Lyrics: "The night is dark, something is watching me"
        Audio: tempo=85, energy=0.4, acousticness=0.8, instrumentalness=0.3
        → {"emotion": "fear", "emotion_intensity": 7.5}
        
        Lyrics: "I feel sick when I see your face"
        Audio: tempo=100, energy=0.5, valence=0.25, speechiness=0.8
        → {"emotion": "disgust", "emotion_intensity": 6.8}
        
        Lyrics: "Something exciting is about to happen, I can feel it"
        Audio: tempo=130, energy=0.75, danceability=0.8, valence=0.7
        → {"emotion": "anticipation", "emotion_intensity": 7.2}
        
        Lyrics: "Mixed emotions, not sure how I feel"
        Audio: tempo=110, energy=0.5, valence=0.5, danceability=0.5
        → {"emotion": "sadness", "emotion_intensity": 5.0}
        '''
        "\nANALYZE BOTH LYRICS AND AUDIO FEATURES. RETURN NOTHING BUT JSON."
    }

def get_prompt(lyrics : str, audio_features : AudioFeatures):
    user = {  # the actual metrics + song lyrics
        "role": "user", 
        "content": f'''
        Song lyrics: {lyrics} 
        Metrics: 

        tempo={audio_features.tempo},
        energy={audio_features.energy},
        danceability={audio_features.danceability},
        acousticness={audio_features.acousticness},
        instrumentalness={audio_features.instrumentalness},
        valence={audio_features.valence},
        key={audio_features.key},
        mode={audio_features.mode},
        loudness={audio_features.loudness},
        speechiness={audio_features.speechiness},
        duration={audio_features.duration}
        '''
    }
    
    return [system, user]
