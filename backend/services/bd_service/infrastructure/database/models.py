from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index, Date, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrackModel(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    text = Column(Text, nullable=False)
    emotion = Column(String(50), nullable=False, index=True)
    emotion_intensity = Column(Float, nullable=False)
    audio_features = Column(JSON, nullable=False)
    release_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_tracks_author_title', 'author', 'title', unique=True),
        Index('idx_tracks_emotion_intensity', 'emotion_intensity'),
        Index('idx_tracks_created_at', 'created_at'),
        CheckConstraint(
            "emotion IN ('happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation')",
            name='valid_emotion'
        ),
        CheckConstraint(
            "emotion_intensity >= 0 AND emotion_intensity <= 10",
            name='valid_intensity'
        ),
    )