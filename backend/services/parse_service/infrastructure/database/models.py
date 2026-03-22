from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TrackMetadataModel(Base):
    __tablename__ = "track_metadata"

    track_id = Column(String(64), primary_key=True)
    source = Column(String(64), nullable=False, default="yandex_music")
    title = Column(String(255), nullable=False)
    main_artist = Column(String(255), nullable=False)
    # Legacy column kept for compatibility with existing shared DB schemas.
    artists = Column(String(512), nullable=True)
    genre = Column(String(128), nullable=True)
    album = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    storage_uri = Column(String(1024), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrackProcessingStatusModel(Base):
    __tablename__ = "track_processing_status"

    track_id = Column(
        String(64),
        ForeignKey("track_metadata.track_id", ondelete="CASCADE"),
        primary_key=True,
    )
    metadata_available = Column(Boolean, nullable=False, default=False)
    audio_available = Column(Boolean, nullable=False, default=False)
    lyrics_available = Column(Boolean, nullable=False, default=False)
    text_available = Column(Boolean, nullable=False, default=False)
    dsp_processed = Column(Boolean, nullable=False, default=False)
    sent_to_llm = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrackAnalysisResultModel(Base):
    __tablename__ = "track_analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(
        String(64),
        ForeignKey("track_metadata.track_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    dsp = Column(JSONB, nullable=True)
    lyrics = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
