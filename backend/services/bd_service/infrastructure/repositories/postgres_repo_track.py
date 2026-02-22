from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from domain.entities.track import Track
from domain.repo.repo_track import TrackRepository
from infrastructure.database.models import TrackModel

class PostgresTrackRepository(TrackRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, track: Track) -> Track:
        """Save track to database"""
        if track.id:  # Update
            stmt = (
                update(TrackModel)
                .where(TrackModel.id == track.id)
                .values(
                    title=track.title,
                    author=track.author,
                    genre=track.genre,
                    text=track.text,
                    emotion=track.emotion,
                    emotion_intensity=track.emotion_intensity,
                    audio_features=track.audio_features
                )
                .returning(TrackModel)
            )
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            track_model = result.scalar_one()
        else:  # Create
            track_model = TrackModel(
                title=track.title,
                author=track.author,
                genre=track.genre,
                text=track.text,
                emotion=track.emotion,
                emotion_intensity=track.emotion_intensity,
                audio_features=track.audio_features
            )
            self.db_session.add(track_model)
            await self.db_session.commit()
            await self.db_session.refresh(track_model)

        return self._to_domain_entity(track_model)

    async def find_by_id(self, track_id: int) -> Optional[Track]:
        """Find track by ID"""
        stmt = select(TrackModel).where(TrackModel.id == track_id)
        result = await self.db_session.execute(stmt)
        track_model = result.scalar_one_or_none()
        
        return self._to_domain_entity(track_model) if track_model else None

    async def find_by_author(self, author: str, limit: int = 50) -> List[Track]:
        """Find tracks by author"""
        stmt = (
            select(TrackModel)
            .where(TrackModel.author.ilike(f"%{author}%"))
            .limit(limit)
            .order_by(TrackModel.created_at.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_by_genre(self, genre: str, limit: int = 50) -> List[Track]:
        """Find tracks by genre"""
        stmt = (
            select(TrackModel)
            .where(TrackModel.genre.ilike(f"%{genre}%"))
            .limit(limit)
            .order_by(TrackModel.created_at.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_by_emotion(
        self, 
        emotion: str, 
        min_intensity: float = 0.0,
        max_intensity: float = 10.0
    ) -> List[Track]:
        """Find tracks by emotion and intensity"""
        stmt = (
            select(TrackModel)
            .where(
                and_(
                    TrackModel.emotion == emotion,
                    TrackModel.emotion_intensity.between(min_intensity, max_intensity)
                )
            )
            .order_by(TrackModel.emotion_intensity.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        
        return [self._to_domain_entity(tm) for tm in track_models]

    async def search_by_text(self, query: str, limit: int = 20) -> List[Track]:
        """Search tracks by text content"""
        # Full-text search in song lyrics
        stmt = (
            select(TrackModel)
            .where(
                or_(
                    TrackModel.text.ilike(f"%{query}%"),
                    TrackModel.title.ilike(f"%{query}%")
                )
            )
            .limit(limit)
            .order_by(TrackModel.created_at.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Track]:
        """Get all tracks with pagination"""
        stmt = (
            select(TrackModel)
            .limit(limit)
            .offset(offset)
            .order_by(TrackModel.created_at.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        
        return [self._to_domain_entity(tm) for tm in track_models]

    async def delete(self, track_id: int) -> bool:
        """Delete track"""
        stmt = delete(TrackModel).where(TrackModel.id == track_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def get_statistics(self) -> Dict[str, Any]:
        """Get track statistics"""
        # Total number of tracks
        total_count = await self.db_session.scalar(select(func.count(TrackModel.id)))
        
        # Statistics by genre
        genre_stats = await self.db_session.execute(
            select(
                TrackModel.genre,
                func.count(TrackModel.id).label('count'),
                func.avg(TrackModel.emotion_intensity).label('avg_intensity')
            )
            .group_by(TrackModel.genre)
        )
        
        # Statistics by emotion
        emotion_stats = await self.db_session.execute(
            select(
                TrackModel.emotion,
                func.count(TrackModel.id).label('count'),
                func.avg(TrackModel.emotion_intensity).label('avg_intensity')
            )
            .group_by(TrackModel.emotion)
        )
        
        # Recently added tracks
        recent_tracks = await self.find_all(limit=10)
        
        return {
            "total_tracks": total_count or 0,
            "genres": [dict(row) for row in genre_stats],
            "emotions": [dict(row) for row in emotion_stats],
            "recent_tracks": recent_tracks,
            "average_intensity": await self.db_session.scalar(
                select(func.avg(TrackModel.emotion_intensity))
            ) or 0.0
        }

    def _to_domain_entity(self, model: TrackModel) -> Track:
        """ORM -> Entity"""
        return Track(
            id=model.id,
            title=model.title,
            author=model.author,
            genre=model.genre,
            text=model.text,
            emotion=model.emotion,
            emotion_intensity=model.emotion_intensity,
            audio_features=model.audio_features,
            created_at=model.created_at,
            updated_at=model.updated_at
        )