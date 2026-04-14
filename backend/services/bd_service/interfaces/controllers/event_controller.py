from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from usecases.event_service import EventService


class CreateEventRequest(BaseModel):
    id: Optional[int] = None
    year: int = Field(..., ge=1900, le=2030)
    event_name: str = Field(..., min_length=2, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year + 5:
            raise ValueError(f'Year cannot be more than 5 years in the future')
        return v
    
    @field_validator('event_name')
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Event name cannot be empty')
        return v.strip()


class UpdateEventRequest(BaseModel):
    year: Optional[int] = Field(None, ge=1900, le=2030)
    event_name: Optional[str] = Field(None, min_length=2, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    
    @field_validator('event_name')
    @classmethod
    def validate_event_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Event name cannot be empty')
        return v.strip() if v else None


class EventResponse(BaseModel):
    id: int
    year: int
    event_name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    decade: Optional[int] = None
    era: Optional[str] = None
    
    class Config:
        from_attributes = True


class EventsByYearResponse(BaseModel):
    year: int
    events: List[EventResponse]
    total_count: int


class AvailableYearsResponse(BaseModel):
    years: List[int]
    total_count: int
    min_year: Optional[int] = None
    max_year: Optional[int] = None


class EventController:
    def __init__(self, event_service: EventService):
        self.event_service = event_service
        self.router = APIRouter(prefix="/events", tags=["events"])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/years", response_model=AvailableYearsResponse)(self.get_available_years)
        self.router.get("/search", response_model=List[EventResponse])(self.search_events)
        self.router.get("/range", response_model=List[EventResponse])(self.get_events_by_range)
        self.router.get("/decade/{decade}", response_model=List[EventResponse])(self.get_events_by_decade)
        self.router.get("/era/{era}", response_model=List[EventResponse])(self.get_events_by_era)
        self.router.get("/statistics", response_model=Dict[str, Any])(self.get_statistics)
        
        self.router.get("/year/{year}", response_model=EventsByYearResponse)(self.get_events_by_year)
        self.router.get("/{event_id}", response_model=EventResponse)(self.get_event)
        
        self.router.post("/", response_model=EventResponse, status_code=201)(self.create_event)
        self.router.put("/{event_id}", response_model=EventResponse)(self.update_event)
        self.router.delete("/{event_id}")(self.delete_event)
        self.router.get("/", response_model=List[EventResponse])(self.list_events)

    async def create_event(self, request: CreateEventRequest) -> EventResponse:
        try:
            event = await self.event_service.create_event(
                year=request.year,
                event_name=request.event_name,
                description=request.description,
                id=request.id
            )
            return self._enrich_event_response(event)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_available_years(self) -> AvailableYearsResponse:
        years = await self.event_service.get_available_years()
        stats = await self.event_service.get_statistics()
        
        return AvailableYearsResponse(
            years=years,
            total_count=len(years),
            min_year=stats.get('min_year'),
            max_year=stats.get('max_year')
        )

    async def get_events_by_year(self, year: int) -> EventsByYearResponse:
        try:
            events = await self.event_service.get_events_by_year(year)
            return EventsByYearResponse(
                year=year,
                events=[self._enrich_event_response(e) for e in events],
                total_count=len(events)
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_events_by_range(
        self,
        year_from: int = Query(..., ge=1900, le=2030, description="Начальный год"),
        year_to: int = Query(..., ge=1900, le=2030, description="Конечный год")
    ) -> List[EventResponse]:
        try:
            events = await self.event_service.get_events_by_year_range(year_from, year_to)
            return [self._enrich_event_response(e) for e in events]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_events_by_decade(self, decade: int) -> List[EventResponse]:
        try:
            events = await self.event_service.get_events_by_decade(decade)
            return [self._enrich_event_response(e) for e in events]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_events_by_era(self, era: str) -> List[EventResponse]:
        try:
            events = await self.event_service.get_events_by_era(era)
            return [self._enrich_event_response(e) for e in events]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_event(self, event_id: int) -> EventResponse:
        try:
            event = await self.event_service.get_event(event_id)
            return self._enrich_event_response(event)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def search_events(
        self,
        q: str = Query(..., min_length=2, description="Поисковый запрос"),
        limit: int = Query(50, ge=1, le=200)
    ) -> List[EventResponse]:
        try:
            events = await self.event_service.search_events(q, limit)
            return [self._enrich_event_response(e) for e in events]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_event(
        self,
        event_id: int,
        request: UpdateEventRequest
    ) -> EventResponse:
        try:
            event = await self.event_service.update_event(
                event_id=event_id,
                year=request.year,
                event_name=request.event_name,
                description=request.description
            )
            return self._enrich_event_response(event)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_event(self, event_id: int) -> Dict[str, str]:
        try:
            success = await self.event_service.delete_event(event_id)
            if success:
                return {"message": f"Event {event_id} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Event not found")
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def list_events(
        self,
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ) -> List[EventResponse]:
        try:
            events = await self.event_service.get_all_events(limit, offset)
            return [self._enrich_event_response(e) for e in events]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_statistics(self) -> Dict[str, Any]:
        return await self.event_service.get_statistics()

    def _enrich_event_response(self, event) -> EventResponse:
        response = EventResponse.model_validate(event)
        response.decade = event.get_decade()
        response.era = event.get_era()
        return response   