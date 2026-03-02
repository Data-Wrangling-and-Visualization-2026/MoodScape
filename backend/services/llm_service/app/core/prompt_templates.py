from app.models.schemas import AudioFeatures


system = { # the role, rules, and output format
        "role": "system", 
        "content": 
        "You are an expert in music emotion analysis."
        "You will get song lyrics and audio features to extract the song primary emotion and emotion intensity"
        "Rules:"
        "1) RETURN ONLY VALID JSON in the format:"
        '''
        {
        "emotion": "anger",
        "emotion_intensity": 0.75
        }
        '''
        "2) Allowed emotions are : ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']."
        "You MUST select only one emotion from the list"
        "emotion_intensity is a float number that ranges from 0 to 10"
        "RETURN NOTHING BUT JSON"
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
