from typing import Optional, List, Dict, Any
from domain.entities.track import Track
from domain.repo.repo_track import TrackRepository

class TrackService:
    def __init__(self, track_repository: TrackRepository):
        self.track_repository = track_repository

    async def create_track(
        self,
        title: str,
        author: str,
        genre: str,
        text: str,
        emotion: str,
        emotion_intensity: float,
        audio_features: Dict[str, Any]
    ) -> Track:
        
        existing_tracks = await self.track_repository.find_by_author(author)
        for track in existing_tracks:
            if track.title.lower() == title.lower():
                raise ValueError(f"Track '{title}' by {author} already exists")

        track = Track(
            id=None,
            title=title.strip(),
            author=author.strip(),
            genre=genre.strip(),
            text=text.strip(),
            emotion=emotion.lower(),
            emotion_intensity=emotion_intensity,
            audio_features=audio_features
        )

        if not track.validate():
            raise ValueError("Invalid track data")

        saved_track = await self.track_repository.save(track)
        return saved_track

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
        return await self.track_repository.find_by_genre(genre, limit)

    async def get_tracks_by_emotion(
        self, 
        emotion: str, 
        min_intensity: float = 0.0,
        max_intensity: float = 10.0
    ) -> List[Track]:
        if emotion not in Track.VALID_EMOTIONS:
            raise ValueError(f"Invalid emotion. Must be one of: {Track.VALID_EMOTIONS}")
        
        if not (0 <= min_intensity <= max_intensity <= 10):
            raise ValueError("Intensity must be between 0 and 10")
        
        return await self.track_repository.find_by_emotion(
            emotion, min_intensity, max_intensity
        )

    async def search_tracks(self, query: str, limit: int = 20) -> List[Track]:
        if len(query.strip()) < 3:
            raise ValueError("Search query must be at least 3 characters")
        
        return await self.track_repository.search_by_text(query, limit)

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

    async def get_track_statistics(self) -> Dict[str, Any]:
        """Get stats """
        stats = await self.track_repository.get_statistics()
        
        if 'tracks' in stats:
            tracks = stats['tracks']
            if tracks:
                genre_intensity = {}
                for track in tracks:
                    if track.genre not in genre_intensity:
                        genre_intensity[track.genre] = []
                    genre_intensity[track.genre].append(track.emotion_intensity)
                
                stats['average_intensity_by_genre'] = {
                    genre: sum(intensities) / len(intensities)
                    for genre, intensities in genre_intensity.items()
                }
                
                intensity_categories = {'low': 0, 'medium': 0, 'high': 0}
                for track in tracks:
                    category = track.get_emotion_category()
                    intensity_categories[category] += 1
                
                stats['intensity_distribution'] = intensity_categories
        
        return stats