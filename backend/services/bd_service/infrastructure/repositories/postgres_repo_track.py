from typing import Optional, List, Dict, Any
from datetime import date, timedelta, datetime
from sqlalchemy import select, update, delete, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities.track import Track
from domain.repo.repo_track import TrackRepository
from infrastructure.database.models import TrackModel


class PostgresTrackRepository(TrackRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, track: Track) -> Track:
        if track.id:
            existing = await self.find_by_id(track.id)
            if existing:
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
                        emotion_components=track.emotion_components,
                        audio_features=track.audio_features,
                        release_date=track.release_date,
                        updated_at=datetime.utcnow()
                    )
                    .returning(TrackModel)
                )
                result = await self.db_session.execute(stmt)
                await self.db_session.commit()
                track_model = result.scalar_one()
            else:
                track_model = TrackModel(
                    id=track.id,
                    title=track.title,
                    author=track.author,
                    genre=track.genre,
                    text=track.text,
                    emotion=track.emotion,
                    emotion_intensity=track.emotion_intensity,
                    emotion_components=track.emotion_components,
                    audio_features=track.audio_features,
                    release_date=track.release_date
                )
                self.db_session.add(track_model)
                await self.db_session.commit()
                await self.db_session.refresh(track_model)
        else:
            track_model = TrackModel(
                title=track.title,
                author=track.author,
                genre=track.genre,
                text=track.text,
                emotion=track.emotion,
                emotion_intensity=track.emotion_intensity,
                emotion_components=track.emotion_components,
                audio_features=track.audio_features,
                release_date=track.release_date
            )
            self.db_session.add(track_model)
            await self.db_session.commit()
            await self.db_session.refresh(track_model)

        return self._to_domain_entity(track_model)

    async def find_by_id(self, track_id: int) -> Optional[Track]:
        stmt = select(TrackModel).where(TrackModel.id == track_id)
        result = await self.db_session.execute(stmt)
        track_model = result.scalar_one_or_none()
        return self._to_domain_entity(track_model) if track_model else None

    async def find_by_author(self, author: str, limit: int = 50) -> List[Track]:
        stmt = (
            select(TrackModel)
            .where(TrackModel.author.ilike(f"%{author}%"))
            .limit(limit)
            .order_by(TrackModel.release_date.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_by_genre(self, genre: str, limit: int = 50) -> List[Track]:
        stmt = (
            select(TrackModel)
            .where(TrackModel.genre.ilike(f"%{genre}%"))
            .limit(limit)
            .order_by(TrackModel.release_date.desc())
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
        stmt = (
            select(TrackModel)
            .where(
                and_(
                    TrackModel.emotion == emotion,
                    TrackModel.emotion_intensity.between(min_intensity, max_intensity)
                )
            )
            .order_by(TrackModel.release_date.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def search_by_text(self, query: str, limit: int = 20) -> List[Track]:
        stmt = (
            select(TrackModel)
            .where(
                or_(
                    TrackModel.text.ilike(f"%{query}%"),
                    TrackModel.title.ilike(f"%{query}%")
                )
            )
            .limit(limit)
            .order_by(
                func.similarity(TrackModel.title, query).desc(),
                TrackModel.release_date.desc()
            )
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Track]:
        stmt = (
            select(TrackModel)
            .limit(limit)
            .offset(offset)
            .order_by(TrackModel.release_date.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_by_release_date_range(
        self, 
        start_date: date, 
        end_date: date,
        limit: int = 100
    ) -> List[Track]:
        stmt = (
            select(TrackModel)
            .where(
                and_(
                    TrackModel.release_date >= start_date,
                    TrackModel.release_date <= end_date
                )
            )
            .limit(limit)
            .order_by(TrackModel.release_date.desc())
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def find_recent_releases(self, days: int = 30, limit: int = 50) -> List[Track]:
        cutoff_date = date.today() - timedelta(days=days)
        return await self.find_by_release_date_range(cutoff_date, date.today(), limit)

    async def find_by_year(self, year: int, limit: int = 100) -> List[Track]:
        stmt = (
            select(TrackModel)
            .where(
                and_(
                    TrackModel.release_date >= date(year, 1, 1),
                    TrackModel.release_date <= date(year, 12, 31)
                )
            )
            .limit(limit)
            .order_by(TrackModel.release_date)
        )
        result = await self.db_session.execute(stmt)
        track_models = result.scalars().all()
        return [self._to_domain_entity(tm) for tm in track_models]

    async def delete(self, track_id: int) -> bool:
        stmt = delete(TrackModel).where(TrackModel.id == track_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def get_statistics(self) -> Dict[str, Any]:
        total_count = await self.db_session.scalar(select(func.count(TrackModel.id)))
        
        genre_stats = await self.db_session.execute(
            select(
                TrackModel.genre,
                func.count(TrackModel.id).label('count'),
                func.avg(TrackModel.emotion_intensity).label('avg_intensity'),
                func.min(TrackModel.release_date).label('oldest_release'),
                func.max(TrackModel.release_date).label('newest_release')
            )
            .group_by(TrackModel.genre)
        )
        
        emotion_stats = await self.db_session.execute(
            select(
                TrackModel.emotion,
                func.count(TrackModel.id).label('count'),
                func.avg(TrackModel.emotion_intensity).label('avg_intensity')
            )
            .group_by(TrackModel.emotion)
        )
        
        year_stats = await self.db_session.execute(
            select(
                func.extract('year', TrackModel.release_date).label('year'),
                func.count(TrackModel.id).label('count')
            )
            .group_by(func.extract('year', TrackModel.release_date))
            .order_by(text('year desc'))
        )
        
        recent_tracks = await self.find_all(limit=10)
        
        date_range = await self.db_session.execute(
            select(
                func.min(TrackModel.release_date).label('earliest_release'),
                func.max(TrackModel.release_date).label('latest_release')
            )
        )
        date_stats = date_range.first()
        
        avg_intensity = await self.db_session.scalar(
            select(func.avg(TrackModel.emotion_intensity))
        ) or 0.0
        
        return {
            "total_tracks": total_count or 0,
            "genres": [dict(row._mapping) for row in genre_stats],
            "emotions": [dict(row._mapping) for row in emotion_stats],
            "years": [dict(row._mapping) for row in year_stats],
            "recent_tracks": [self._to_domain_entity(t) for t in recent_tracks],
            "average_intensity": float(avg_intensity),
            "earliest_release": date_stats.earliest_release if date_stats else None,
            "latest_release": date_stats.latest_release if date_stats else None
        }
    
    async def get_distinct_genres(self) -> List[str]:
        stmt = select(TrackModel.genre).distinct().order_by(TrackModel.genre)
        result = await self.db_session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_distinct_years(self) -> List[int]:
        stmt = select(func.distinct(func.extract('year', TrackModel.release_date)).label('year')).order_by('year')
        result = await self.db_session.execute(stmt)
        return [int(row[0]) for row in result.all()]

    def _to_domain_entity(self, model: TrackModel) -> Track:
        return Track(
            id=model.id,
            title=model.title,
            author=model.author,
            genre=model.genre,
            text=model.text,
            emotion=model.emotion,
            emotion_intensity=model.emotion_intensity,
            emotion_components=model.emotion_components,
            audio_features=model.audio_features,
            release_date=model.release_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )