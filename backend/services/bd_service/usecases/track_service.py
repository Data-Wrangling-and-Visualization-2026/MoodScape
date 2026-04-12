from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from domain.entities.track import Track
from domain.repo.repo_track import TrackRepository


class TrackService:
    def __init__(self, track_repository: TrackRepository):
        self.track_repository = track_repository

    async def create_track(
        self,
        id: int,
        title: str,
        author: str,
        genre: str,
        text: str,
        emotion: str,
        emotion_intensity: float,
        emotion_components: List[Dict[str, Any]],
        audio_features: Dict[str, Any],
        release_date: date
        ) -> Track:

        existing_tracks = await self.track_repository.find_by_author(author)
        for track in existing_tracks:
            if track.title.lower() == title.lower():
                raise ValueError(f"Track '{title}' by {author} already exists")

        if release_date > date.today():
            raise ValueError("Release date cannot be in the future")

        track = Track(
            id=id,
            title=title.strip(),
            author=author.strip(),
            genre=genre.strip(),
            text=text.strip(),
            emotion=emotion.lower(),
            emotion_intensity=emotion_intensity,
            emotion_components=emotion_components,
            audio_features=audio_features,
            release_date=release_date
        )

        if not track.validate():
            raise ValueError("Invalid track data")

        saved_track = await self.track_repository.save(track)
        return saved_track
    
    async def filter_tracks(
        self,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        emotion: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "release_date",
        sort_order: str = "desc"
    ) -> List[Track]:
        valid_emotions = {'happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'}
        if emotion and emotion not in valid_emotions:
            raise ValueError(f"Invalid emotion. Must be one of: {valid_emotions}")
        if year and (year < 1900 or year > date.today().year + 1):
            raise ValueError(f"Invalid year")
        if search and len(search.strip()) < 3:
            raise ValueError("Search query must be at least 3 characters")

        return await self.track_repository.filter(
            genre=genre,
            year=year,
            emotion=emotion,
            search=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )    

    async def get_track(self, track_id: int) -> Track:
        if track_id <= 0:
            raise ValueError("Invalid track ID")

        track = await self.track_repository.find_by_id(track_id)
        if not track:
            raise ValueError(f"Track with ID {track_id} not found")
        
        return track

    async def get_tracks_by_author(self, author: str, limit: int = 50) -> List[Track]:
        if len(author.strip()) < 2:
            raise ValueError("Author name must be at least 2 characters")
        
        return await self.track_repository.find_by_author(author, limit)

    async def get_tracks_by_genre(self, genre: str, limit: int = 50) -> List[Track]:
        if len(genre.strip()) < 2:
            raise ValueError("Genre must be at least 2 characters")
        
        return await self.track_repository.find_by_genre(genre, limit)

    async def get_tracks_by_emotion(
        self, 
        emotion: str, 
        min_intensity: float = 0.0,
        max_intensity: float = 10.0
    ) -> List[Track]:
        valid_emotions = {'happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'}
        if emotion not in valid_emotions:
            raise ValueError(f"Invalid emotion. Must be one of: {valid_emotions}")
        
        if not (0 <= min_intensity <= max_intensity <= 10):
            raise ValueError("Intensity must be between 0 and 10")
        
        return await self.track_repository.find_by_emotion(
            emotion, min_intensity, max_intensity
        )

    async def search_tracks(self, query: str, limit: int = 20) -> List[Track]:
        if len(query.strip()) < 3:
            raise ValueError("Search query must be at least 3 characters")
        
        return await self.track_repository.search_by_text(query, limit)
    
    async def get_unique_genres(self) -> List[str]:
        return await self.track_repository.get_distinct_genres()

    async def get_unique_years(self) -> List[int]:
        return await self.track_repository.get_distinct_years()

    async def delete_track(self, track_id: int) -> bool:
        track = await self.get_track(track_id)
        return await self.track_repository.delete(track_id)

    async def get_tracks_by_intensity_range(
        self, 
        min_intensity: float, 
        max_intensity: float,
        limit: int = 50
    ) -> List[Track]:
        if not (0 <= min_intensity <= max_intensity <= 10):
            raise ValueError("Intensity must be between 0 and 10")
        
        all_tracks = await self.track_repository.find_all(limit=1000)
        return [
            track for track in all_tracks 
            if min_intensity <= track.emotion_intensity <= max_intensity
        ][:limit]

    async def get_tracks_by_release_year(self, year: int, limit: int = 100) -> List[Track]:
        if year < 1900 or year > date.today().year + 1:
            raise ValueError(f"Invalid year. Must be between 1900 and {date.today().year + 1}")
        
        return await self.track_repository.find_by_year(year, limit)

    async def get_recent_releases(self, days: int = 30, limit: int = 50) -> List[Track]:
        if days < 1:
            raise ValueError("Days must be positive")
        
        return await self.track_repository.find_recent_releases(days, limit)

    async def get_tracks_by_release_date_range(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100
    ) -> List[Track]:
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        
        if end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        return await self.track_repository.find_by_release_date_range(
            start_date, end_date, limit
        )

    async def get_tracks_by_decade(self, decade: int, limit: int = 200) -> List[Track]:
        if decade < 1900 or decade % 10 != 0:
            raise ValueError("Decade must be a year ending with 0 (e.g., 1990, 2000)")
        
        start_date = date(decade, 1, 1)
        end_date = date(decade + 9, 12, 31)
        
        return await self.get_tracks_by_release_date_range(start_date, end_date, limit)

    async def get_tracks_by_era(self, era: str, limit: int = 100) -> List[Track]:
        eras = {
            "classic": (date(1950, 1, 1), date(1979, 12, 31)),
            "eighties": (date(1980, 1, 1), date(1989, 12, 31)),
            "nineties": (date(1990, 1, 1), date(1999, 12, 31)),
            "two_thousands": (date(2000, 1, 1), date(2009, 12, 31)),
            "twenty_tens": (date(2010, 1, 1), date(2019, 12, 31)),
            "twenty_twenties": (date(2020, 1, 1), date.today())
        }
        
        if era.lower() not in eras:
            raise ValueError(f"Invalid era. Choose from: {list(eras.keys())}")
        
        start_date, end_date = eras[era.lower()]
        return await self.get_tracks_by_release_date_range(start_date, end_date, limit)

    async def update_track_release_date(self, track_id: int, new_release_date: date) -> Track:
        track = await self.get_track(track_id)
        
        if new_release_date > date.today():
            raise ValueError("Release date cannot be in the future")
        
        updated_track = Track(
            id=track.id,
            title=track.title,
            author=track.author,
            genre=track.genre,
            text=track.text,
            emotion=track.emotion,
            emotion_intensity=track.emotion_intensity,
            audio_features=track.audio_features,
            release_date=new_release_date,
            created_at=track.created_at,
            updated_at=datetime.utcnow()
        )
        
        return await self.track_repository.save(updated_track)

    async def get_track_statistics(self) -> Dict[str, Any]:
        stats = await self.track_repository.get_statistics()
        
        if 'recent_tracks' in stats:
            recent_tracks = stats['recent_tracks']
            
            today = date.today()
            age_categories = {
                'new_releases': 0,
                'recent': 0,
                'old': 0,
                'classic': 0
            }
            
            for track in recent_tracks:
                if track.release_date:
                    years_old = (today - track.release_date).days / 365.25
                    if years_old < 1:
                        age_categories['new_releases'] += 1
                    elif years_old < 3:
                        age_categories['recent'] += 1
                    elif years_old < 10:
                        age_categories['old'] += 1
                    else:
                        age_categories['classic'] += 1
            
            stats['age_distribution'] = age_categories
        
        if stats.get('earliest_release'):
            earliest_tracks = await self.get_tracks_by_release_year(
                stats['earliest_release'].year, limit=1
            )
            if earliest_tracks:
                stats['oldest_track'] = {
                    'id': earliest_tracks[0].id,
                    'title': earliest_tracks[0].title,
                    'author': earliest_tracks[0].author,
                    'release_date': earliest_tracks[0].release_date
                }
        
        if stats.get('latest_release'):
            latest_tracks = await self.get_tracks_by_release_year(
                stats['latest_release'].year, limit=1
            )
            if latest_tracks:
                stats['newest_track'] = {
                    'id': latest_tracks[0].id,
                    'title': latest_tracks[0].title,
                    'author': latest_tracks[0].author,
                    'release_date': latest_tracks[0].release_date
                }
        
        return stats