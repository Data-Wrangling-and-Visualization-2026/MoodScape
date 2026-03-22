from fastapi import APIRouter, Request
import asyncio
from app.models.schemas import TrackCSV
from app.core.llm_analyser import LlmAnalyser
from app.clients.bd_client import BdClient
from datetime import date


router = APIRouter()
llm_analyser = LlmAnalyser()
bd_client = BdClient()


@router.get("/health")
async def check_health():
    return {
        "service": "LLM",
        "status": "healthy",
    }


@router.post("/analyze")
async def analyze_track(request: Request, track_data: TrackCSV):
    """
    Добавляет трек в очередь на обработку
    """
    try:
        pipeline = request.app.state.pipeline
        audio_features = track_data.to_audio_features()
        release_date = date(track_data.year, 1, 1)
        
        track_dict = {
            "id": track_data.id,
            "title": track_data.title,
            "author": track_data.main_artist,
            "genre": track_data.genre,
            "text": track_data.lyrics,
            "audio_features": audio_features,
            "release_date": release_date
        }
        
        # Добавляем в очередь pipeline
        await pipeline.message_queue.put(track_dict)
        
        return {
            "status": "accepted",
            "track_id": track_data.id,
            "message": "Track added to processing queue"
        }
        
    except Exception as e:
        print(f"Error adding track to queue: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/queue/status")
async def get_queue_status(request: Request):
    pipeline = request.app.state.pipeline
    return {
        "queue_size": pipeline.message_queue.qsize(),
        "is_running": pipeline.is_running
    }