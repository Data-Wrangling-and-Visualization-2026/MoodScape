from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from backend.services.parse_service.infrastructure.database.models import (
    TrackAnalysisResultModel,
    TrackMetadataModel,
    TrackProcessingStatusModel,
)


class ParseTrackRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        """Store SQLAlchemy session factory used by all repository operations."""
        self._session_factory = session_factory

    def _get_or_create_status(self, session: Session, track_id: str) -> TrackProcessingStatusModel:
        """Load processing status row or create a default one for a track."""
        status = session.get(TrackProcessingStatusModel, track_id)
        if status is None:
            status = TrackProcessingStatusModel(track_id=track_id)
            session.add(status)
        return status

    def upsert_metadata(
        self,
        *,
        track_id: str,
        title: str,
        main_artist: str,
        album: str | None,
        duration_ms: int | None,
        storage_uri: str | None,
        genre: str | None = None,
        year: int | None = None,
        source: str = "yandex_music",
    ) -> None:
        """
        Insert or update track metadata and ensure status row exists.

        Notes:
        - `main_artist` is the canonical metadata field used by parse_service.
        - Legacy `artists` column is mirrored for backward DB compatibility.
        """
        session = self._session_factory()
        try:
            metadata = session.get(TrackMetadataModel, track_id)
            if metadata is None:
                metadata = TrackMetadataModel(track_id=track_id)

            metadata.title = title
            metadata.main_artist = main_artist
            # Keep legacy column populated in shared DB schemas where it is still NOT NULL.
            metadata.artists = main_artist
            metadata.album = album
            metadata.duration_ms = duration_ms
            metadata.storage_uri = storage_uri
            metadata.genre = genre
            metadata.year = year
            metadata.source = source
            metadata.updated_at = datetime.utcnow()

            session.add(metadata)
            self._get_or_create_status(session, track_id)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_status(
        self,
        track_id: str,
        *,
        metadata_available: bool | None = None,
        audio_available: bool | None = None,
        lyrics_available: bool | None = None,
        dsp_processed: bool | None = None,
        sent_to_llm: bool | None = None,
        error_message: str | None = None,
    ) -> None:
        """Patch selected status flags for one track in a single transaction."""
        session = self._session_factory()
        try:
            status = self._get_or_create_status(session, track_id)
            if metadata_available is not None:
                status.metadata_available = metadata_available
            if audio_available is not None:
                status.audio_available = audio_available
            if lyrics_available is not None:
                status.lyrics_available = lyrics_available
                status.text_available = lyrics_available
            if dsp_processed is not None:
                status.dsp_processed = dsp_processed
            if sent_to_llm is not None:
                status.sent_to_llm = sent_to_llm
            status.error_message = error_message
            status.updated_at = datetime.utcnow()

            session.add(status)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_analysis(
        self,
        track_id: str,
        *,
        dsp: dict | None = None,
        lyrics: str | None = None,
    ) -> None:
        """Create/update analysis row with DSP payload and/or cleaned lyrics text."""
        session = self._session_factory()
        try:
            analysis = (
                session.query(TrackAnalysisResultModel)
                .filter(TrackAnalysisResultModel.track_id == track_id)
                .one_or_none()
            )
            if analysis is None:
                analysis = TrackAnalysisResultModel(track_id=track_id)

            if dsp is not None:
                analysis.dsp = dsp
            if lyrics is not None:
                analysis.lyrics = lyrics
            analysis.updated_at = datetime.utcnow()

            session.add(analysis)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        """Convert datetime values to ISO-8601 strings for API responses."""
        return value.isoformat() if value else None

    def get_track_bundle(self, track_id: str) -> dict | None:
        """Return merged metadata, processing status, and analysis for one track."""
        session = self._session_factory()
        try:
            metadata = session.get(TrackMetadataModel, track_id)
            if metadata is None:
                return None

            status = session.get(TrackProcessingStatusModel, track_id)
            analysis = (
                session.query(TrackAnalysisResultModel)
                .filter(TrackAnalysisResultModel.track_id == track_id)
                .one_or_none()
            )
            resolved_main_artist = metadata.main_artist or metadata.artists or "unknown"

            return {
                "metadata": {
                    "track_id": metadata.track_id,
                    "source": metadata.source,
                    "title": metadata.title,
                    "main_artist": resolved_main_artist,
                    "genre": metadata.genre,
                    "album": metadata.album,
                    "year": metadata.year,
                    "duration_ms": metadata.duration_ms,
                    "storage_uri": metadata.storage_uri,
                },
                "status": {
                    "metadata_available": bool(status and status.metadata_available),
                    "audio_available": bool(status and status.audio_available),
                    "lyrics_available": bool(
                        status and (status.lyrics_available or status.text_available)
                    ),
                    "dsp_processed": bool(status and status.dsp_processed),
                    "sent_to_llm": bool(status and status.sent_to_llm),
                    "error_message": status.error_message if status else None,
                    "updated_at": self._serialize_datetime(status.updated_at) if status else None,
                },
                "analysis": {
                    "dsp": analysis.dsp if analysis else None,
                    "lyrics": analysis.lyrics if analysis else None,
                    "updated_at": self._serialize_datetime(analysis.updated_at) if analysis else None,
                },
            }
        finally:
            session.close()

    def list_tracks_without_lyrics(self, limit: int = 100) -> list[dict]:
        """List bundles where metadata exists but lyrics are still missing."""
        session = self._session_factory()
        try:
            rows = (
                session.query(TrackMetadataModel.track_id)
                .join(
                    TrackProcessingStatusModel,
                    TrackProcessingStatusModel.track_id == TrackMetadataModel.track_id,
                )
                .filter(
                    TrackProcessingStatusModel.metadata_available.is_(True),
                    TrackProcessingStatusModel.lyrics_available.is_(False),
                )
                .limit(limit)
                .all()
            )
            output: list[dict] = []
            for row in rows:
                bundle = self.get_track_bundle(row.track_id)
                if bundle is not None:
                    output.append(bundle)
            return output
        finally:
            session.close()

    def list_track_status(
        self,
        *,
        track_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Return paginated admin status rows ordered by latest metadata update."""
        session = self._session_factory()
        try:
            query = (
                session.query(TrackMetadataModel, TrackProcessingStatusModel)
                .outerjoin(
                    TrackProcessingStatusModel,
                    TrackProcessingStatusModel.track_id == TrackMetadataModel.track_id,
                )
                .order_by(TrackMetadataModel.updated_at.desc())
            )

            if track_id:
                query = query.filter(TrackMetadataModel.track_id == track_id)

            rows = query.offset(offset).limit(limit).all()
            items: list[dict] = []
            for metadata, status in rows:
                resolved_main_artist = metadata.main_artist or metadata.artists or "unknown"
                items.append(
                    {
                        "track_id": metadata.track_id,
                        "title": metadata.title,
                        "main_artist": resolved_main_artist,
                        "metadata_available": bool(status and status.metadata_available),
                        "audio_available": bool(status and status.audio_available),
                        "lyrics_available": bool(
                            status and (status.lyrics_available or status.text_available)
                        ),
                        "dsp_processed": bool(status and status.dsp_processed),
                        "sent_to_llm": bool(status and status.sent_to_llm),
                        "error_message": status.error_message if status else None,
                        "updated_at": self._serialize_datetime(status.updated_at) if status else None,
                    }
                )
            return items
        finally:
            session.close()
