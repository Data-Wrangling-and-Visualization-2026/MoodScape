from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from infrastructure.database.postgres import PostgresDatabase
from infrastructure.repositories.postgres_repo_track import PostgresTrackRepository
from infrastructure.repositories.postgres_repo_event import PostgresEventRepository
from usecases.track_service import TrackService
from usecases.event_service import EventService
from interfaces.controllers.track_controller import TrackController
from interfaces.controllers.event_controller import EventController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = PostgresDatabase()
track_service = None
event_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global track_service, event_service
    logger.info("Starting up...")
    try:
        await db.initialize()
        logger.info("Database connected successfully")
        
        async for session in db.get_session():
            track_repository = PostgresTrackRepository(session)
            event_repository = PostgresEventRepository(session)
            
            track_service = TrackService(track_repository)
            event_service = EventService(event_repository)
            
            track_controller = TrackController(track_service)
            event_controller = EventController(event_service)
            
            app.include_router(track_controller.router)
            app.include_router(event_controller.router)
            
            logger.info("Track routes registered successfully")
            logger.info("Event routes registered successfully")
            break
            
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await db.close()
    logger.info("Database connection closed")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Track Service API",
        description="Microservice for storing and managing music tracks with emotional characteristics and historical events",
        version="1.0.0",
        lifespan=lifespan, 
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "service": "Track Service",
            "version": "1.0.0",
            "status": "operational",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "endpoints": {
                "tracks": "/tracks",
                "events": "/events",
                "docs": "/docs",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health_check():
        if track_service is None or event_service is None:
            return {
                "status": "starting",
                "database": "initializing",
                "services": {
                    "track": track_service is not None,
                    "event": event_service is not None
                }
            }
        try:
            async for _ in db.get_session():
                break
            return {
                "status": "healthy",
                "database": "connected",
                "services": {
                    "track": "ready",
                    "event": "ready"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )