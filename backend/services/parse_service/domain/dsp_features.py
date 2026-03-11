from dataclasses import dataclass

@dataclass
class DSPFeatures:
    tempo: float
    danceability: float
    energy: float
    acousticness: float
    instrumentalness: float
    valence: float
    loudness: float
    key: int
    mode: int
    speechiness: float
    duration_ms: int
