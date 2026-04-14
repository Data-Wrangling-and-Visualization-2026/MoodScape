from typing import List, Dict, Any, Optional
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, field_validator
from usecases.track_service import TrackService

class AudioFeatures(BaseModel):
    tempo: float = Field(..., gt=0)
    energy: float = Field(..., ge=0.0, le=1.0)
    danceability: float = Field(..., ge=0.0, le=1.0)
    acousticness: float = Field(..., ge=0.0, le=1.0)
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)
    key: int = Field(..., ge=0, le=11)
    mode: int = Field(..., ge=0, le=1)
    loudness: float = Field(..., gt=0.0)
    speechiness: float = Field(..., ge=0.0, le=1.0)
    duration: float = Field(..., gt=0.0)

class CreateTrackRequest(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=2, max_length=255)
    genre: str = Field(..., min_length=2, max_length=100)
    text: str = Field(..., min_length=1)
    emotion: str = Field(..., min_length=2, max_length=50)        
    emotion_intensity: float = Field(..., ge=0, le=10)              
    emotion_components: List[Dict[str, Any]] = Field(..., description="Список {emotion, weight}")
    audio_features: AudioFeatures
    release_date: date

    @field_validator('emotion')
    @classmethod
    def validate_emotion(cls, v: str) -> str:
        valid = {'happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation'}
        if v.lower() not in valid:
            raise ValueError(f'Emotion must be one of: {valid}')
        return v.lower()

class UpdateTrackRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, min_length=2, max_length=100)
    emotion: Optional[str] = Field(None, min_length=2, max_length=50)
    emotion_intensity: Optional[float] = Field(None, ge=0, le=10)
    release_date: Optional[date] = None

    @field_validator('release_date')
    @classmethod
    def validate_release_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            if v > date.today():
                raise ValueError('Release date cannot be in the future')
            if v < date(1900, 1, 1):
                raise ValueError('Release date cannot be before 1900')
        return v

class TrackResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    text: str
    emotion: str
    emotion_intensity: float
    emotion_components: List[Dict[str, Any]]
    audio_features: Dict[str, Any]
    release_date: date
    created_at: datetime
    updated_at: Optional[datetime]
    average_score: Optional[float] = None
    year: Optional[int] = None

    class Config:
        from_attributes = True


class TrackController:
    def __init__(self, track_service: TrackService):
        self.track_service = track_service
        self.router = APIRouter(prefix="/tracks", tags=["tracks"])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/genres", response_model=List[str])(self.get_genres)
        self.router.get("/years", response_model=List[int])(self.get_years)
        self.router.get("/filter/", response_model=List[TrackResponse])(self.filter_tracks)
        self.router.get("/search/", response_model=List[TrackResponse])(self.search_tracks)
        self.router.get("/by-author/{author}", response_model=List[TrackResponse])(self.get_tracks_by_author)
        self.router.get("/by-genre/{genre}", response_model=List[TrackResponse])(self.get_tracks_by_genre)
        self.router.get("/by-emotion/{emotion}", response_model=List[TrackResponse])(self.get_tracks_by_emotion)
        self.router.get("/by-year/{year}", response_model=List[TrackResponse])(self.get_tracks_by_year)
        self.router.get("/recent/", response_model=List[TrackResponse])(self.get_recent_releases)
        self.router.get("/by-decade/{decade}", response_model=List[TrackResponse])(self.get_tracks_by_decade)
        self.router.get("/by-era/{era}", response_model=List[TrackResponse])(self.get_tracks_by_era)
        self.router.get("/by-date-range/", response_model=List[TrackResponse])(self.get_tracks_by_date_range)
        self.router.get("/statistics/", response_model=Dict[str, Any])(self.get_statistics)

        
        self.router.get("/{track_id}", response_model=TrackResponse)(self.get_track)
        
        self.router.post("/", response_model=TrackResponse)(self.create_track)
        self.router.put("/{track_id}", response_model=TrackResponse)(self.update_track)
        self.router.delete("/{track_id}")(self.delete_track)
        self.router.get("/", response_model=List[TrackResponse])(self.list_tracks)


    async def create_track(self, request: CreateTrackRequest) -> TrackResponse:
        try:
            track = await self.track_service.create_track(
                id=request.id,
                title=request.title,
                author=request.author,
                genre=request.genre,
                text=request.text,
                emotion=request.emotion,
                emotion_intensity=request.emotion_intensity,
                emotion_components=request.emotion_components,
                audio_features=request.audio_features.model_dump(),
                release_date=request.release_date
            )
            return self._enrich_track_response(track)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    async def filter_tracks(
        self,
        genre: Optional[str] = Query(None, min_length=2, max_length=100),
        year_from: Optional[int] = Query(None, ge=1900, le=date.today().year + 1, description="Year from"),
        year_to: Optional[int] = Query(None, ge=1900, le=date.today().year + 1, description="Year to"),
        emotion: Optional[str] = Query(None, min_length=2, max_length=50),
        search: Optional[str] = Query(None, min_length=3),
        limit: Optional[int] = Query(None, ge=1, le=10000),
        offset: Optional[int] = Query(None, ge=0),
        sort_by: str = Query("release_date", pattern="^(release_date|created_at|title|author|emotion_intensity)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$")
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.filter_tracks(
                genre=genre,
                year_from=year_from,
                year_to=year_to,
                emotion=emotion,
                search=search,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_track(self, track_id: int) -> TrackResponse:
        try:
            track = await self.track_service.get_track(track_id)
            return self._enrich_track_response(track)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
    async def get_genres(self) -> List[str]:
        return await self.track_service.get_unique_genres()

    async def get_years(self) -> List[int]:
        return await self.track_service.get_unique_years()

    async def update_track(
        self, 
        track_id: int, 
        request: UpdateTrackRequest
    ) -> TrackResponse:
        try:
            track = await self.track_service.get_track(track_id)
            
            if request.title:
                track.title = request.title
            if request.genre:
                track.genre = request.genre
            if request.emotion:
                track.emotion = request.emotion
            if request.emotion_intensity is not None:
                track.emotion_intensity = request.emotion_intensity
            if request.release_date:
                updated_track = await self.track_service.update_track_release_date(
                    track_id, request.release_date
                )
            else:
                updated_track = await self.track_service.track_repository.save(track)
            
            return self._enrich_track_response(updated_track)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_track(self, track_id: int) -> Dict[str, str]:
        try:
            success = await self.track_service.delete_track(track_id)
            if success:
                return {"message": f"Track {track_id} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Track not found")
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def list_tracks(
        self,
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        sort_by: str = Query("release_date", pattern="^(release_date|created_at|title|author)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$")
    ) -> List[TrackResponse]:
        tracks = await self.track_service.track_repository.find_all(
            limit=limit, 
            offset=offset
        )
        
        if sort_by == "release_date":
            tracks.sort(key=lambda t: t.release_date, reverse=(sort_order == "desc"))
        elif sort_by == "created_at":
            tracks.sort(key=lambda t: t.created_at or datetime.min, reverse=(sort_order == "desc"))
        elif sort_by == "title":
            tracks.sort(key=lambda t: t.title.lower(), reverse=(sort_order == "desc"))
        elif sort_by == "author":
            tracks.sort(key=lambda t: t.author.lower(), reverse=(sort_order == "desc"))
        
        return [self._enrich_track_response(track) for track in tracks]

    async def search_tracks(
        self,
        q: str = Query(..., min_length=3, description="Search query"),
        limit: int = Query(20, ge=1, le=100)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.search_tracks(q, limit)
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tracks_by_author(
        self,
        author: str,
        limit: int = Query(50, ge=1, le=200)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.get_tracks_by_author(author, limit)
        return [self._enrich_track_response(track) for track in tracks]

    async def get_tracks_by_genre(
        self,
        genre: str,
        limit: int = Query(50, ge=1, le=200)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.get_tracks_by_genre(genre, limit)
        return [self._enrich_track_response(track) for track in tracks]

    async def get_tracks_by_emotion(
        self,
        emotion: str,
        min_intensity: float = Query(0.0, ge=0, le=10),
        max_intensity: float = Query(10.0, ge=0, le=10)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.get_tracks_by_emotion(
                emotion, min_intensity, max_intensity
            )
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tracks_by_year(
        self,
        year: int,
        limit: int = Query(100, ge=1, le=500)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.get_tracks_by_release_year(year, limit)
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_recent_releases(
        self,
        days: int = Query(30, ge=1, le=365, description="Number of days"),
        limit: int = Query(50, ge=1, le=200)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.get_recent_releases(days, limit)
        return [self._enrich_track_response(track) for track in tracks]

    async def get_tracks_by_decade(
        self,
        decade: int,
        limit: int = Query(200, ge=1, le=1000)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.get_tracks_by_decade(decade, limit)
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tracks_by_era(
        self,
        era: str,
        limit: int = Query(100, ge=1, le=500)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.get_tracks_by_era(era, limit)
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tracks_by_date_range(
        self,
        start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
        limit: int = Query(100, ge=1, le=500)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.get_tracks_by_release_date_range(
                start_date, end_date, limit
            )
            return [self._enrich_track_response(track) for track in tracks]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_statistics(self) -> Dict[str, Any]:
        return await self.track_service.get_track_statistics()

    def _enrich_track_response(self, track) -> TrackResponse:
        response = TrackResponse.model_validate(track)
        response.average_score = track.calculate_average_score()
        response.year = track.release_date.year if track.release_date else None
        return response