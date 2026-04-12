from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Literal, Tuple, Dict, Any
from datetime import date, datetime

class AudioFeatures(BaseModel):
    tempo: float = Field(gt=0)
    energy: float = Field(ge=0.0, le=1.0)
    danceability: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)
    key: float = Field(ge=0.0, le=11.0)
    mode: float = Field(ge=0.0, le=1.0)
    loudness: float = Field(gt=0.0)
    speechiness: float = Field(ge=0.0, le=1.0)
    duration: float = Field(gt=0.0)

class MixedEmotion(BaseModel):
    emotion: Literal['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
    weight: float = Field(ge=0.0, le=1.0)

class EmotionVector(BaseModel):
    components: List[MixedEmotion] = Field(min_length=1)
    intensity: float = Field(ge=0.0, le=10.0)

    @model_validator(mode='after')
    def weights_sum_to_one(self):
        total = sum(c.weight for c in self.components)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f'Sum of weights must be 1.0, got {total}')
        return self

    def get_coordinates(self) -> Tuple[float, float]:
        base = {
            'happiness': (1.0, 1.0),
            'anger': (1.0, 0.0),
            'fear': (-1.0, -1.0),
            'sadness': (-1.0, 0.0),
            'disgust': (0.0, -1.0),
            'anticipation': (0.0, 1.0)
        }
        x = sum(base[c.emotion][0] * c.weight for c in self.components)
        y = sum(base[c.emotion][1] * c.weight for c in self.components)
        factor = self.intensity / 10.0
        return (x * factor, y * factor)

    def get_dominant_emotion(self) -> str:
        if len(self.components) == 1:
            return self.components[0].emotion
        return max(self.components, key=lambda c: c.weight).emotion

class TrackGet(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    text: str
    audio_features: AudioFeatures
    release_date: datetime

class TrackPost(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    text: str
    emotion: str                           
    emotion_intensity: float = Field(ge=0.0, le=10.0)
    emotion_components: List[Dict[str, Any]]  # [{"emotion": "anger", "weight": 0.7}, ...]
    audio_features: AudioFeatures
    release_date: date

    model_config = ConfigDict(from_attributes=True)

class LlmResponse(BaseModel):
    emotion_vector: EmotionVector

class TrackCSV(BaseModel):
    id: int
    track_id: int
    lyrics: str = Field(default="")
    title: str
    main_artist: str
    artists: str
    genre: str
    album: str
    year: int = Field(default=0)
    duration_ms: int
    mode: int
    tempo: float
    energy: float
    valence: float
    loudness: float
    speechiness: float
    acousticness: float
    danceability: float
    instrumentalness: float

    def to_audio_features(self) -> AudioFeatures:
        return AudioFeatures(
            tempo=self.tempo,
            energy=self.energy,
            danceability=self.danceability,
            acousticness=self.acousticness,
            instrumentalness=self.instrumentalness,
            valence=self.valence,
            key=0.0,
            mode=float(self.mode),
            loudness=abs(self.loudness),
            speechiness=self.speechiness,
            duration=self.duration_ms / 1000.0
        )