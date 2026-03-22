import os
import logging

import essentia.standard as es

from backend.services.parse_service.domain.dsp_features import DSPFeatures
from backend.services.parse_service.infrastructure.database.postgres import PostgresDatabase
from backend.services.parse_service.infrastructure.dsp_models.feature_extractor import (
    HighLevelFeatureExtractor,
)
from backend.services.parse_service.infrastructure.genius_client import GeniusClient
from backend.services.parse_service.infrastructure.llm_client import LLMClient
from backend.services.parse_service.infrastructure.repositories.track_repository import (
    ParseTrackRepository,
)
from backend.services.parse_service.infrastructure.yandex_client import YandexMusicClient
import yandex_music


class ParseTracksUseCase:
    def __init__(
        self,
        *,
        database: PostgresDatabase | None = None,
        track_repository: ParseTrackRepository | None = None,
        llm_client: LLMClient | None = None,
    ):
        """Wire external clients, storage path, and persistence dependencies."""
        self.yandex = YandexMusicClient()
        self.genius = GeniusClient()
        self.llm = llm_client or LLMClient()
        self.highlevel = HighLevelFeatureExtractor()

        self.database = database or PostgresDatabase()
        self.track_repository = track_repository or ParseTrackRepository(
            self.database.get_session
        )
        self.audio_root = os.path.abspath(os.getenv("LOCAL_AUDIO_STORAGE_PATH", "storage"))
        os.makedirs(self.audio_root, exist_ok=True)

        self.llm_push_enabled = os.getenv("LLM_PUSH_ENABLED", "false").lower() == "true"
        self._db_initialized = False
        self._logger = logging.getLogger(__name__)

    def _ensure_db_ready(self) -> None:
        """Initialize DB tables lazily before first persistence call."""
        if self._db_initialized:
            return

        self.database.initialize()
        self._db_initialized = True

    def _clean_lyrics(self, lyrics: str | None) -> str | None:
        """Normalize raw lyrics text and remove noisy Genius boilerplate."""
        if not lyrics:
            return None

        import re

        text = lyrics.replace("\n", " ")
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"You might also like.*", "", text)
        text = re.sub(r"\d+ Contributors.*Lyrics", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text if text else None

    def analyze_audio(
        self, file_path: str, yandex_duration_ms: int | None = None
    ) -> DSPFeatures:
        """Extract low/high-level DSP features from a local audio file."""
        extractor = es.MusicExtractor(
            lowlevelStats=["mean"],
            rhythmStats=["mean"],
            tonalStats=["mean"],
        )

        features, _ = extractor(file_path)
        highlevel = self.highlevel.extract(file_path)

        def safe_get(pool, key, default=0):
            """Read a descriptor safely when it may be missing in the pool."""
            return pool[key] if key in pool.descriptorNames() else default

        key_map = {
            "C": 0,
            "C#": 1,
            "D": 2,
            "D#": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "G": 7,
            "G#": 8,
            "A": 9,
            "A#": 10,
            "B": 11,
        }

        return DSPFeatures(
            tempo=float(safe_get(features, "rhythm.bpm")),
            danceability=highlevel["danceability"],
            energy=float(safe_get(features, "lowlevel.average_loudness")),
            acousticness=highlevel["acousticness"],
            instrumentalness=highlevel["instrumentalness"],
            valence=highlevel["valence"],
            loudness=float(safe_get(features, "lowlevel.loudness_ebu128.momentary.mean")),
            key=key_map.get(safe_get(features, "tonal.key_temperley.key")),
            mode=1 if safe_get(features, "tonal.key_temperley.scale") == "major" else 0,
            speechiness=highlevel["speechiness"],
            duration_ms=int(yandex_duration_ms or 0),
        )

    @staticmethod
    def _extract_main_artist(track) -> str:
        """Extract artist name from Yandex track object."""
        names = [
            artist.name.strip()
            for artist in (track.artists or [])
            if getattr(artist, "name", None)
        ]
        if not names:
            return "unknown"
        return names[0]

    @classmethod
    def _extract_metadata(cls, track, *, storage_uri: str | None) -> dict:
        """Map Yandex track object into metadata payload used by repository."""
        album_obj = track.albums[0] if track.albums else None
        album_title = album_obj.title if album_obj else None
        album_year = getattr(album_obj, "year", None) if album_obj else None

        return {
            "track_id": str(track.id),
            "title": track.title,
            "main_artist": cls._extract_main_artist(track),
            "genre": getattr(album_obj, "genre", None),
            "album": album_title,
            "year": int(album_year) if album_year else None,
            "duration_ms": track.duration_ms,
            "storage_uri": storage_uri,
        }

    @staticmethod
    def _bundle_to_llm_payload(bundle: dict) -> dict:
        """Convert persisted bundle into payload expected by llm_service."""
        metadata = bundle["metadata"]
        analysis = bundle.get("analysis") or {}

        return {
            "track_id": metadata["track_id"],
            "metadata": {
                "title": metadata["title"],
                "main_artist": metadata["main_artist"],
                "genre": metadata.get("genre"),
                "album": metadata.get("album"),
                "year": metadata.get("year"),
                "duration_ms": metadata.get("duration_ms"),
            },
            "lyrics": analysis.get("lyrics"),
            "dsp": analysis.get("dsp"),
        }

    def _prepare_llm_payload(self, bundle: dict) -> dict | None:
        """
        Prepare payload for llm_service in the required format (TrackCSV model).
        """
        metadata = bundle["metadata"]
        analysis = bundle.get("analysis") or {}
        dsp_data = analysis.get("dsp", {})
        
        # Get lyrics from analysis
        lyrics = analysis.get("lyrics")
        if not lyrics:
            return None
        
        # Prepare the payload in the exact format expected by TrackCSV model
        payload = {
            "id": int(metadata["track_id"]),  # TrackCSV expects 'id' field
            "track_id": int(metadata["track_id"]),  # Also has track_id field
            "lyrics": lyrics,
            "title": metadata["title"],
            "main_artist": metadata["main_artist"],
            "artists": metadata["main_artist"],
            "genre": metadata.get("genre") or "",
            "album": metadata.get("album") or "",
            "year": metadata.get("year") or 0,
            "duration_ms": metadata.get("duration_ms") or 0,
            # DSP features
            "mode": dsp_data.get("mode", 0),
            "tempo": dsp_data.get("tempo", 0.0),
            "energy": dsp_data.get("energy", 0.0),
            "valence": dsp_data.get("valence", 0.0),
            "loudness": dsp_data.get("loudness", 0.0),
            "speechiness": dsp_data.get("speechiness", 0.0),
            "acousticness": dsp_data.get("acousticness", 0.0),
            "danceability": dsp_data.get("danceability", 0.0),
            "instrumentalness": dsp_data.get("instrumentalness", 0.0),
        }
        
        return payload

    def _check_and_send_to_llm(self, track_id: str) -> None:
        """
        Check if all data is available after DSP analysis.
        If yes - send to LLM, if no - do nothing.
        """
        if not self.llm_push_enabled:
            return

        try:
            bundle = self.track_repository.get_track_bundle(track_id)
            if bundle is None:
                return

            status = bundle["status"]
            metadata = bundle["metadata"]
            analysis = bundle.get("analysis") or {}
            
            # Check if ALL required data is available
            all_data_ready = (
                status["metadata_available"] and
                status["audio_available"] and
                status["dsp_processed"] and
                status["lyrics_available"] and
                not status["sent_to_llm"] and
                metadata.get("title") and
                metadata.get("main_artist") and
                analysis.get("lyrics") is not None and
                analysis.get("dsp") is not None
            )
            
            if not all_data_ready:
                # Data not ready, do nothing
                self._logger.debug(f"Track {track_id}: not all data ready for LLM")
                return

            # All data is ready, prepare and send payload
            payload = self._prepare_llm_payload(bundle)
            if not payload:
                self._logger.warning(f"Failed to prepare payload for track_id={track_id}")
                return

            # Send to LLM service
            success = self.llm.send_for_analysis(payload)
            
            if success:
                self.track_repository.update_status(
                    track_id,
                    sent_to_llm=True,
                    error_message=None,
                )
                self._logger.info(f"Successfully sent track {track_id} to LLM service")
            else:
                # Failed to send, but we don't retry - just log
                self._logger.error(f"Failed to send track {track_id} to LLM service")
                self.track_repository.update_status(
                    track_id,
                    sent_to_llm=False,
                    error_message="Failed to send to LLM service (will not retry)"
                )
                    
        except Exception as e:
            self._logger.exception(f"Error checking/sending to LLM for track {track_id}: {e}")

    def _maybe_notify_llm(self, track_id: str) -> None:
        """
        Notify llm_service only when the full payload is ready (DSP + lyrics + metadata).
        """
        if not self.llm_push_enabled:
            return

        try:
            bundle = self.track_repository.get_track_bundle(track_id)
            if bundle is None:
                self._logger.debug(f"Bundle not found for track_id={track_id}")
                return

            status = bundle["status"]
            metadata = bundle["metadata"]
            analysis = bundle.get("analysis") or {}
            
            # Check if all required data is available
            ready = (
                status["metadata_available"] and
                status["audio_available"] and
                status["dsp_processed"] and
                status["lyrics_available"] and
                not status["sent_to_llm"] and
                metadata.get("title") and
                metadata.get("main_artist") and
                analysis.get("lyrics") is not None and
                analysis.get("dsp") is not None
            )
            
            if not ready:
                # Log what's missing for debugging
                missing = []
                if not status["metadata_available"]: missing.append("metadata")
                if not status["audio_available"]: missing.append("audio")
                if not status["dsp_processed"]: missing.append("dsp")
                if not status["lyrics_available"]: missing.append("lyrics")
                if status["sent_to_llm"]: missing.append("already_sent")
                if not metadata.get("title"): missing.append("title")
                if not metadata.get("main_artist"): missing.append("main_artist")
                if analysis.get("lyrics") is None: missing.append("lyrics_data")
                if analysis.get("dsp") is None: missing.append("dsp_data")
                
                self._logger.debug(
                    f"Track {track_id} not ready for LLM. Missing: {missing}"
                )
                return

            # Prepare payload in the required format
            payload = self._prepare_llm_payload(bundle)
            if not payload:
                self._logger.warning(
                    f"Failed to prepare payload for track_id={track_id}"
                )
                return

            # Send to LLM service
            success = self.llm.send_for_analysis(payload)
            
            if success:
                self.track_repository.update_status(
                    track_id,
                    sent_to_llm=True,
                    error_message=None,
                )
                self._logger.info(f"Successfully sent track {track_id} to LLM service")
            else:
                error_msg = f"Failed to send track {track_id} to LLM service"
                self.track_repository.update_status(
                    track_id,
                    sent_to_llm=False,
                    error_message=error_msg,
                )
                self._logger.error(error_msg)
                
        except Exception as e:
            self._logger.exception(f"Error notifying LLM for track {track_id}: {e}")
            self.track_repository.update_status(
                track_id,
                error_message=f"LLM notification error: {str(e)}"
            )

        
    def _build_local_audio_path(self, track_id: str, extension: str = "mp3") -> str:
        """Build deterministic path for storing a downloaded audio file."""
        return os.path.join(self.audio_root, f"{track_id}.{extension}")

    def _persist_track_results(self, track_id: str, track, local_audio_path: str) -> dict:
        """Persist metadata/audio/DSP for a track parsed from Yandex."""
        metadata = self._extract_metadata(track, storage_uri=local_audio_path)
        self.track_repository.upsert_metadata(**metadata)
        self.track_repository.update_status(
            track_id,
            metadata_available=True,
            audio_available=True,
            error_message=None,
        )

        # Extract DSP features
        dsp = self.analyze_audio(
            local_audio_path,
            yandex_duration_ms=metadata.get("duration_ms"),
        )
        
        # Try to get lyrics from Yandex Music
        lyrics = None
        has_lyrics = False
        
        try:
            lyrics = self.yandex.get_lyrics(track_id=track_id)
            clean_lyrics = self._clean_lyrics(lyrics)
            has_lyrics = bool(clean_lyrics)
            
            # Save both DSP and lyrics
            self.track_repository.save_analysis(
                track_id, 
                dsp=dsp.__dict__, 
                lyrics=clean_lyrics
            )
            
            self._logger.info(f"Track {track_id}: DSP processed, lyrics={'found' if has_lyrics else 'not found'}")
            
        except yandex_music.exceptions.NotFoundError:
            # No lyrics available in Yandex
            self.track_repository.save_analysis(track_id, dsp=dsp.__dict__, lyrics=None)
            self._logger.info(f"Track {track_id}: DSP processed, no lyrics available")
            
        except Exception as e:
            # Other errors during lyrics fetch
            self._logger.exception(f"Error fetching lyrics for {track_id}: {e}")
            self.track_repository.save_analysis(track_id, dsp=dsp.__dict__, lyrics=None)

        # Update DSP and lyrics status
        self.track_repository.update_status(
            track_id,
            dsp_processed=True,
            lyrics_available=has_lyrics,
            error_message=None if has_lyrics else "No lyrics available"
        )
        
        # AFTER DSP and lyrics are processed - check if we can send to LLM
        self._check_and_send_to_llm(track_id)
        
        return self.track_repository.get_track_bundle(track_id)
    
    def _fetch_and_store_lyrics(
        self,
        *,
        track_id: str,
        title: str,
        main_artist: str,
    ) -> str | None:
        """
        Fetch lyrics from Genius, normalize text, and persist analysis/status fields.

        Returns cleaned lyrics when found, otherwise `None`.
        """
        try:
            lyrics = self.yandex.get_lyrics(track_id=track_id)
            clean_lyrics = self._clean_lyrics(lyrics)

            self.track_repository.save_analysis(track_id, lyrics=clean_lyrics)
            self.track_repository.update_status(
                track_id,
                lyrics_available=bool(clean_lyrics),
                error_message=None,
            )

            if clean_lyrics:
                self._maybe_notify_llm(track_id)
            return clean_lyrics
        except Exception as exc:
            self._logger.exception("Lyrics fetch failed for track_id=%s", track_id)
            self.track_repository.update_status(track_id, error_message=str(exc))
            return None

    def execute_parse(self) -> None:
        """
        Parse current chart tracks and persist metadata/audio/DSP.
        """
        self._ensure_db_ready()

        tracks = self.yandex.get_discovery_tracks()
        if not tracks:
            return

        for chart_track in tracks:
            track_id = str(chart_track.id)
            existing = self.track_repository.get_track_bundle(track_id)
            if existing and existing["status"]["audio_available"] and existing["status"]["dsp_processed"]:
                continue

            try:
                local_audio_path = self._build_local_audio_path(track_id)
                downloaded_track = self.yandex.download_track(track_id, local_audio_path)
                self._persist_track_results(track_id, downloaded_track, local_audio_path)
            except Exception as exc:
                self._logger.exception("Track parse failed for track_id=%s", track_id)
                try:
                    self.track_repository.update_status(track_id, error_message=str(exc))
                except Exception:
                    pass

    def execute_single(self, track_id: str) -> dict:
        """Parse one track by ID, including lyrics fetch, and return updated bundle."""
        self._ensure_db_ready()

        normalized_track_id = str(track_id)
        local_audio_path = self._build_local_audio_path(normalized_track_id)
        downloaded_track = self.yandex.download_track(normalized_track_id, local_audio_path)
        bundle = self._persist_track_results(
            normalized_track_id,
            downloaded_track,
            local_audio_path,
        )

        metadata = bundle["metadata"]
        self._fetch_and_store_lyrics(
            track_id=normalized_track_id,
            title=metadata["title"],
            main_artist=metadata["main_artist"],
        )
        return self.track_repository.get_track_bundle(normalized_track_id)

    def execute_lyrics_backfill(self, limit: int = 100) -> None:
        """
        Fill lyrics for tracks that already have metadata but no lyrics.
        """
        self._ensure_db_ready()

        bundles = self.track_repository.list_tracks_without_lyrics(limit=limit)
        for bundle in bundles:
            track_id = bundle["metadata"]["track_id"]
            title = bundle["metadata"]["title"]
            artist = (bundle["metadata"]["main_artist"] or "").strip()
            self._fetch_and_store_lyrics(
                track_id=track_id,
                title=title,
                main_artist=artist,
            )

    def get_track_bundle(self, track_id: str) -> dict | None:
        """Fetch combined metadata/status/analysis by track ID."""
        self._ensure_db_ready()
        return self.track_repository.get_track_bundle(str(track_id))

    def get_track_payload_for_llm(self, track_id: str) -> dict | None:
        """
        Return payload for llm_service only when all required data is ready.
        """
        bundle = self.get_track_bundle(track_id)
        if bundle is None:
            return None

        status = bundle["status"]
        ready = (
            status["metadata_available"]
            and status["audio_available"]
            and status["dsp_processed"]
            and status["lyrics_available"]
        )
        if not ready:
            return None

        return self._bundle_to_llm_payload(bundle)

    def list_track_status(
        self,
        *,
        track_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Return processing statuses for admin panel."""
        self._ensure_db_ready()
        return self.track_repository.list_track_status(
            track_id=track_id,
            limit=limit,
            offset=offset,
        )

    def health(self) -> dict:
        """Check DB connectivity and schema readiness for service health."""
        db_connected, db_error = self.database.check_connection()
        schema_ready = False
        schema_error = None

        if db_connected:
            try:
                self.database.initialize()
                self._db_initialized = True
                schema_ready = True
            except Exception as exc:
                schema_error = str(exc)

        is_healthy = db_connected and schema_ready
        return {
            "service": "parse_service",
            "status": "healthy" if is_healthy else "unhealthy",
            "database": {
                "connected": db_connected,
                "connection_error": db_error,
                "schema_ready": schema_ready,
                "schema_error": schema_error,
            },
        }
