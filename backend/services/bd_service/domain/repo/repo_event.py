from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from domain.entities.event import Event


class EventRepository(ABC):
    @abstractmethod
    async def save(self, event: Event) -> Event:
        pass

    @abstractmethod
    async def find_by_id(self, event_id: int) -> Optional[Event]:
        pass

    @abstractmethod
    async def find_by_year(self, year: int) -> List[Event]:
        pass

    @abstractmethod
    async def find_by_year_range(self, year_from: int, year_to: int) -> List[Event]:
        pass

    @abstractmethod
    async def get_all_years(self) -> List[int]:
        pass

    @abstractmethod
    async def search_by_name(self, query: str, limit: int = 50) -> List[Event]:
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Event]:
        pass

    @abstractmethod
    async def delete(self, event_id: int) -> bool:
        pass

    @abstractmethod
    async def get_statistics(self) -> dict:
        pass