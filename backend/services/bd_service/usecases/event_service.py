from typing import Optional, List, Dict, Any
from datetime import date
from domain.entities.event import Event
from domain.repo.repo_event import EventRepository


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    async def create_event(
        self,
        year: int,
        event_name: str,
        description: Optional[str] = None,
        id: Optional[int] = None
    ) -> Event:
        event = Event(
            id=id,
            year=year,
            event_name=event_name.strip(),
            description=description.strip() if description else None
        )
        
        if not event.validate():
            raise ValueError("Invalid event data")
        
        existing_events = await self.event_repository.find_by_year(year)
        for existing in existing_events:
            if existing.event_name.lower() == event_name.lower():
                raise ValueError(f"Event '{event_name}' already exists for year {year}")
        
        return await self.event_repository.save(event)

    async def get_event(self, event_id: int) -> Event:
        if event_id <= 0:
            raise ValueError("Invalid event ID")
        
        event = await self.event_repository.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event with ID {event_id} not found")
        
        return event

    async def get_events_by_year(self, year: int) -> List[Event]:
        if not (Event.MIN_YEAR <= year <= Event.MAX_YEAR):
            raise ValueError(f"Year must be between {Event.MIN_YEAR} and {Event.MAX_YEAR}")
        
        return await self.event_repository.find_by_year(year)

    async def get_events_by_year_range(self, year_from: int, year_to: int) -> List[Event]:
        if year_from > year_to:
            raise ValueError("year_from must be <= year_to")
        
        if not (Event.MIN_YEAR <= year_from <= Event.MAX_YEAR):
            raise ValueError(f"year_from must be between {Event.MIN_YEAR} and {Event.MAX_YEAR}")
        
        if not (Event.MIN_YEAR <= year_to <= Event.MAX_YEAR):
            raise ValueError(f"year_to must be between {Event.MIN_YEAR} and {Event.MAX_YEAR}")
        
        return await self.event_repository.find_by_year_range(year_from, year_to)

    async def get_available_years(self) -> List[int]:
        return await self.event_repository.get_all_years()

    async def search_events(self, query: str, limit: int = 50) -> List[Event]:
        if len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        return await self.event_repository.search_by_name(query, limit)

    async def get_events_by_decade(self, decade: int) -> List[Event]:
        if decade < 1900 or decade % 10 != 0:
            raise ValueError("Decade must be a year ending with 0 (e.g., 1950, 1960)")
        
        year_from = decade
        year_to = decade + 9
        
        return await self.get_events_by_year_range(year_from, year_to)

    async def get_events_by_era(self, era: str) -> List[Event]:
        eras = {
            "post_war": (1945, 1959),
            "cold_war": (1960, 1979),
            "late_soviet": (1980, 1991),
            "nineties": (1992, 1999),
            "two_thousands": (2000, 2009),
            "twenty_tens": (2010, 2019),
            "twenty_twenties": (2020, 2029)
        }
        
        era_lower = era.lower()
        if era_lower not in eras:
            raise ValueError(f"Invalid era. Choose from: {list(eras.keys())}")
        
        year_from, year_to = eras[era_lower]
        return await self.get_events_by_year_range(year_from, year_to)

    async def update_event(
        self,
        event_id: int,
        year: Optional[int] = None,
        event_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Event:
        event = await self.get_event(event_id)
        
        if year is not None:
            event.year = year
        if event_name is not None:
            event.event_name = event_name.strip()
        if description is not None:
            event.description = description.strip() if description else None
        
        if not event.validate():
            raise ValueError("Invalid event data after update")
        
        return await self.event_repository.save(event)

    async def delete_event(self, event_id: int) -> bool:
        await self.get_event(event_id)
        return await self.event_repository.delete(event_id)

    async def get_all_events(self, limit: int = 100, offset: int = 0) -> List[Event]:
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValueError("Offset must be >= 0")
        
        return await self.event_repository.find_all(limit, offset)

    async def get_statistics(self) -> Dict[str, Any]:
        return await self.event_repository.get_statistics()