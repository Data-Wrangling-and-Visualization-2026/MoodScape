from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.entities.track import Track


class TrackRepository(ABC):
    @abstractmethod
    async def save(self, track: Track) -> Track:
        """Save track"""
        pass

    @abstractmethod
    async def find_by_id(self, track_id: int) -> Optional[Track]:
        """Find track by ID"""
        pass

    @abstractmethod
    async def find_by_author(self, author: str, limit: int = 50) -> List[Track]:
        """Find tracks by author"""
        pass

    @abstractmethod
    async def find_by_genre(self, genre: str, limit: int = 50) -> List[Track]:
        """Find tracks by genre"""
        pass

    @abstractmethod
    async def find_by_emotion(self, emotion: str, min_intensity: float = 0.0, 
                             max_intensity: float = 10.0) -> List[Track]:
        """Find tracks by emotion and intensity"""
        pass

    @abstractmethod
    async def search_by_text(self, query: str, limit: int = 20) -> List[Track]:
        """Find tracks by text (?)"""
        # may be it will not be inclduded
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Track]:
        """Get tracks with pagination"""
        pass

    @abstractmethod
    async def delete(self, track_id: int) -> bool:
        """Simle delete"""
        pass

    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get stats"""
        pass

    @abstractmethod
    async def filter(
        self,
        genre: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        emotion: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "release_date",
        sort_order: str = "desc"
    ) -> List[Track]:
        pass