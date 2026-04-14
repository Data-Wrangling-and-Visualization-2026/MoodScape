from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update, delete, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities.event import Event
from domain.repo.repo_event import EventRepository
from infrastructure.database.models import EventModel


class PostgresEventRepository(EventRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, event: Event) -> Event:
        if event.id:
            existing = await self.find_by_id(event.id)
            if existing:
                stmt = (
                    update(EventModel)
                    .where(EventModel.id == event.id)
                    .values(
                        year=event.year,
                        event_name=event.event_name,
                        description=event.description,
                        updated_at=datetime.utcnow()
                    )
                    .returning(EventModel)
                )
                result = await self.db_session.execute(stmt)
                await self.db_session.commit()
                event_model = result.scalar_one()
            else:
                event_model = EventModel(
                    id=event.id,
                    year=event.year,
                    event_name=event.event_name,
                    description=event.description
                )
                self.db_session.add(event_model)
                await self.db_session.commit()
                await self.db_session.refresh(event_model)
        else:
            event_model = EventModel(
                year=event.year,
                event_name=event.event_name,
                description=event.description
            )
            self.db_session.add(event_model)
            await self.db_session.commit()
            await self.db_session.refresh(event_model)

        return self._to_domain_entity(event_model)

    async def find_by_id(self, event_id: int) -> Optional[Event]:
        stmt = select(EventModel).where(EventModel.id == event_id)
        result = await self.db_session.execute(stmt)
        event_model = result.scalar_one_or_none()
        return self._to_domain_entity(event_model) if event_model else None

    async def find_by_year(self, year: int) -> List[Event]:
        stmt = (
            select(EventModel)
            .where(EventModel.year == year)
            .order_by(EventModel.event_name)
        )
        result = await self.db_session.execute(stmt)
        event_models = result.scalars().all()
        return [self._to_domain_entity(em) for em in event_models]

    async def find_by_year_range(self, year_from: int, year_to: int) -> List[Event]:
        stmt = (
            select(EventModel)
            .where(
                and_(
                    EventModel.year >= year_from,
                    EventModel.year <= year_to
                )
            )
            .order_by(EventModel.year, EventModel.event_name)
        )
        result = await self.db_session.execute(stmt)
        event_models = result.scalars().all()
        return [self._to_domain_entity(em) for em in event_models]

    async def get_all_years(self) -> List[int]:
        stmt = (
            select(EventModel.year)
            .order_by(EventModel.year.desc())
        )
        result = await self.db_session.execute(stmt)
        return [int(row[0]) for row in result.all()]

    async def search_by_name(self, query: str, limit: int = 50) -> List[Event]:
        stmt = (
            select(EventModel)
            .where(EventModel.event_name.ilike(f"%{query}%"))
            .limit(limit)
            .order_by(EventModel.year.desc())
        )
        result = await self.db_session.execute(stmt)
        event_models = result.scalars().all()
        return [self._to_domain_entity(em) for em in event_models]

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Event]:
        stmt = (
            select(EventModel)
            .limit(limit)
            .offset(offset)
            .order_by(EventModel.year.desc(), EventModel.event_name)
        )
        result = await self.db_session.execute(stmt)
        event_models = result.scalars().all()
        return [self._to_domain_entity(em) for em in event_models]

    async def delete(self, event_id: int) -> bool:
        stmt = delete(EventModel).where(EventModel.id == event_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def get_statistics(self) -> dict:
        total_count = await self.db_session.scalar(select(func.count(EventModel.id)))
        
        years_count = await self.db_session.execute(
            select(
                EventModel.year,
                func.count(EventModel.id).label('count')
            )
            .group_by(EventModel.year)
            .order_by(EventModel.year.desc())
        )
        
        decade_expr = func.floor(EventModel.year / 10).label('decade')
        decades_count = await self.db_session.execute(
            select(
                decade_expr,
                func.count(EventModel.id).label('count')
            )
            .group_by('decade')      
            .order_by(text('decade DESC')) 
        )
        
        year_range = await self.db_session.execute(
            select(
                func.min(EventModel.year).label('min_year'),
                func.max(EventModel.year).label('max_year')
            )
        )
        range_stats = year_range.first()
        
        return {
            "total_events": total_count or 0,
            "years_with_events": len([r for r in years_count]),
            "events_by_year": [dict(row._mapping) for row in years_count],
            "events_by_decade": [
                {"decade": int(row.decade) * 10, "count": row.count} 
                for row in decades_count
            ],
            "min_year": range_stats.min_year if range_stats else None,
            "max_year": range_stats.max_year if range_stats else None
        }

    def _to_domain_entity(self, model: EventModel) -> Event:
        return Event(
            id=model.id,
            year=model.year,
            event_name=model.event_name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )