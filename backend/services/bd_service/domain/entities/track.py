from dataclasses import dataclass, field
from datetime import datetime,date
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
    audio_features: Dict[str, Any]  # Contains numeric chars (density, tempo etc)
    release_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    #Const for validation
    # to be changed according the wheel of Emotions
    VALID_EMOTIONS = {'joy', 'sadness', 'anger', 'fear', 'surprise', 'love', 'calm', 'energy'}
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
            
        # Necessary audio features (might be changed)
        required_features = {'density', 'tempo', 'energy', 'danceability'}
        if not all(feature in self.audio_features for feature in required_features):
            return False
        
        return True

    def calculate_average_score(self) -> float:
        """Avg value of track"""
        if not self.audio_features:
            return 0.0
        
        scores = []
        if 'density' in self.audio_features:
            scores.append(self.audio_features['density'])
        if 'energy' in self.audio_features:
            scores.append(self.audio_features['energy'])
        if 'danceability' in self.audio_features:
            scores.append(self.audio_features['danceability'])
        
        return sum(scores) / len(scores) if scores else 0.0

    def get_emotion_category(self) -> str:
        """Category by the emotion intensity"""
        if self.emotion_intensity < 3.0:
            return "low"
        elif self.emotion_intensity < 7.0:
            return "medium"
        else:
            return "high"