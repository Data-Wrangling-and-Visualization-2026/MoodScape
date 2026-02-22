from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrackModel(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    text = Column(Text, nullable=False)
    emotion = Column(String(50), nullable=False, index=True)
    emotion_intensity = Column(Float, nullable=False)
    audio_features = Column(JSON, nullable=False)  # Хранит density и другие характеристики
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_tracks_author_title', 'author', 'title', unique=True),
    )