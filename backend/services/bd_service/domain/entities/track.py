from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import re

@dataclass
class Track:
    """Main entity of music track"""
    id: Optional[int]
    title: str
    author: str
    genre: str
    text: str
    emotion: str
    emotion_intensity: float
    audio_features: Dict[str, Any]  # Contains numeric chars (tempo, energy, danceability etc)
    release_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Updated emotions list
    VALID_EMOTIONS = {'happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'}
    MAX_INTENSITY = 10.0
    MIN_INTENSITY = 0.0

    def validate(self) -> bool:
        if not self.title or len(self.title.strip()) < 1:
            return False
        
        if not self.author or len(self.author.strip()) < 1:
            return False
        
        if not self.genre or len(self.genre.strip()) < 1:
            return False
        
        if self.emotion not in self.VALID_EMOTIONS:
            return False
        
        if not (self.MIN_INTENSITY <= self.emotion_intensity <= self.MAX_INTENSITY):
            return False
        
        if not self.audio_features:
            return False
            
        # Updated required audio features
        required_features = {'tempo', 'energy', 'danceability', 'acousticness', 
                           'instrumentalness', 'valence', 'key', 'mode', 
                           'loudness', 'speechiness', 'duration'}
        if not all(feature in self.audio_features for feature in required_features):
            missing = [f for f in required_features if f not in self.audio_features]
            print(f"Missing required audio features: {missing}")
            return False
        
        return True

    def calculate_average_score(self) -> float:
        """Avg value of track based on energy, danceability and valence"""
        if not self.audio_features:
            return 0.0
        
        scores = []
        if 'energy' in self.audio_features:
            scores.append(self.audio_features['energy'])
        if 'danceability' in self.audio_features:
            scores.append(self.audio_features['danceability'])
        if 'valence' in self.audio_features:
            scores.append(self.audio_features['valence'])
        
        return sum(scores) / len(scores) if scores else 0.0

    def get_emotion_category(self) -> str:
        """Category by the emotion intensity"""
        if self.emotion_intensity < 3.0:
            return "low"
        elif self.emotion_intensity < 7.0:
            return "medium"
        else:
            return "high"