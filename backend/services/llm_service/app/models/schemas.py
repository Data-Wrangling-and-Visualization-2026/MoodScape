from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal
from datetime import date, datetime


class AudioFeatures(BaseModel):
    tempo : float = Field(gt=0)
    energy : float = Field(ge=0.0, le=1.0)
    danceability : float = Field(ge=0.0, le=1.0)
    acousticness : float = Field(ge=0.0, le=1.0)
    instrumentalness : float = Field(ge=0.0, le=1.0)
    valence : float = Field(ge=0.0, le=1.0)
    key : float = Field(ge=0.0, le=11.0)
    mode : float = Field(ge=0.0, le=1.0)
    loudness : float = Field(gt=0.0)
    speechiness : float = Field(ge=0.0, le=1.0)
    duration : float = Field(gt=0.0)
    

class TrackGet(BaseModel):
    id : int
    title : str
    author : str
    genre : str
    text : str
    audio_features : AudioFeatures
    release_date : datetime

class TrackPost(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    text: str
    emotion: Literal['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
    emotion_intensity: float = Field(ge=0.0, le=10.0)
    audio_features: AudioFeatures
    release_date: date
    
    model_config = ConfigDict(from_attributes=True)


class LlmResponse(BaseModel):
    emotion : Literal['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
    emotion_intensity: float = Field(ge=0.0, le=10.0)    

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
    mode: int  # 0 or 1
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
            duration=self.duration_ms / 1000.0  # conv to seconds
        )
    
    model_config = ConfigDict(from_attributes=True)