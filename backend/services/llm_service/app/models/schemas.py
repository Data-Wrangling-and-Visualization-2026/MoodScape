from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class AudioFeatures(BaseModel):
    tempo : int = Field(gt=0)
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
    id : int
    title : str
    author : str
    genre : str
    text : str
    emotion : Literal['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
    emotion_intensity: float = Field(ge=0.0, le=10.0)
    audio_features : AudioFeatures
    release_date : datetime


class LlmResponse(BaseModel):
    emotion : Literal['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
    emotion_intensity: float = Field(ge=0.0, le=10.0)    