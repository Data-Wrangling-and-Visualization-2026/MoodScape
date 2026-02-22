from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from usecases.track_service import TrackService

class AudioFeatures(BaseModel):
    density: float = Field(..., ge=0, le=10, description="Плотность звука")
    tempo: float = Field(..., ge=0, le=300, description="Темп BPM")
    energy: float = Field(..., ge=0, le=10, description="Энергичность")
    danceability: float = Field(..., ge=0, le=10, description="Танцевальность")
    acousticness: Optional[float] = Field(0, ge=0, le=10)
    instrumentalness: Optional[float] = Field(0, ge=0, le=10)
    liveness: Optional[float] = Field(0, ge=0, le=10)
    valence: Optional[float] = Field(0, ge=0, le=10, description="Позитивность")

class CreateTrackRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=2, max_length=255)
    genre: str = Field(..., min_length=2, max_length=100)
    text: str = Field(..., min_length=1)
    emotion: str = Field(..., min_length=2, max_length=50)
    emotion_intensity: float = Field(..., ge=0, le=10)
    audio_features: AudioFeatures

    @validator('emotion')
    def validate_emotion(cls, v):
        valid_emotions = {'joy', 'sadness', 'anger', 'fear', 'surprise', 'love', 'calm', 'energy'}
        if v.lower() not in valid_emotions:
            raise ValueError(f'Emotion must be one of: {valid_emotions}')
        return v.lower()

class UpdateTrackRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, min_length=2, max_length=100)
    emotion: Optional[str] = Field(None, min_length=2, max_length=50)
    emotion_intensity: Optional[float] = Field(None, ge=0, le=10)

class TrackResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    text: str
    emotion: str
    emotion_intensity: float
    audio_features: Dict[str, Any]
    created_at: str
    updated_at: Optional[str]
    average_score: Optional[float] = None

    class Config:
        from_attributes = True

class TrackController:
    def __init__(self, track_service: TrackService):
        self.track_service = track_service
        self.router = APIRouter(prefix="/tracks", tags=["tracks"])
        self._register_routes()

    def _register_routes(self):
        self.router.post("/", response_model=TrackResponse)(self.create_track)
        self.router.get("/{track_id}", response_model=TrackResponse)(self.get_track)
        self.router.put("/{track_id}", response_model=TrackResponse)(self.update_track)
        self.router.delete("/{track_id}")(self.delete_track)
        self.router.get("/", response_model=List[TrackResponse])(self.list_tracks)
        self.router.get("/search/", response_model=List[TrackResponse])(self.search_tracks)
        self.router.get("/by-author/{author}", response_model=List[TrackResponse])(self.get_tracks_by_author)
        self.router.get("/by-genre/{genre}", response_model=List[TrackResponse])(self.get_tracks_by_genre)
        self.router.get("/by-emotion/{emotion}", response_model=List[TrackResponse])(self.get_tracks_by_emotion)
        self.router.get("/statistics/", response_model=Dict[str, Any])(self.get_statistics)

    async def create_track(self, request: CreateTrackRequest) -> TrackResponse:
        try:
            track = await self.track_service.create_track(
                title=request.title,
                author=request.author,
                genre=request.genre,
                text=request.text,
                emotion=request.emotion,
                emotion_intensity=request.emotion_intensity,
                audio_features=request.audio_features.dict()
            )
            response = TrackResponse.from_orm(track)
            response.average_score = track.calculate_average_score()
            return response
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_track(self, track_id: int) -> TrackResponse:
        try:
            track = await self.track_service.get_track(track_id)
            response = TrackResponse.from_orm(track)
            response.average_score = track.calculate_average_score()
            return response
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

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
            
            updated_track = await self.track_service.track_repository.save(track)
            response = TrackResponse.from_orm(updated_track)
            response.average_score = updated_track.calculate_average_score()
            return response
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
        offset: int = Query(0, ge=0)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.track_repository.find_all(
            limit=limit, 
            offset=offset
        )
        responses = []
        for track in tracks:
            response = TrackResponse.from_orm(track)
            response.average_score = track.calculate_average_score()
            responses.append(response)
        return responses

    async def search_tracks(
        self,
        q: str = Query(..., min_length=3, description="Поисковый запрос"),
        limit: int = Query(20, ge=1, le=100)
    ) -> List[TrackResponse]:
        try:
            tracks = await self.track_service.search_tracks(q, limit)
            responses = []
            for track in tracks:
                response = TrackResponse.from_orm(track)
                response.average_score = track.calculate_average_score()
                responses.append(response)
            return responses
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tracks_by_author(
        self,
        author: str,
        limit: int = Query(50, ge=1, le=200)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.get_tracks_by_author(author, limit)
        responses = []
        for track in tracks:
            response = TrackResponse.from_orm(track)
            response.average_score = track.calculate_average_score()
            responses.append(response)
        return responses

    async def get_tracks_by_genre(
        self,
        genre: str,
        limit: int = Query(50, ge=1, le=200)
    ) -> List[TrackResponse]:
        tracks = await self.track_service.get_tracks_by_genre(genre, limit)
        responses = []
        for track in tracks:
            response = TrackResponse.from_orm(track)
            response.average_score = track.calculate_average_score()
            responses.append(response)
        return responses

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
            responses = []
            for track in tracks:
                response = TrackResponse.from_orm(track)
                response.average_score = track.calculate_average_score()
                responses.append(response)
            return responses
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_statistics(self) -> Dict[str, Any]:
        return await self.track_service.get_track_statistics()