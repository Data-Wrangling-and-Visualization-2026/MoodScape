import logging
from threading import Thread

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.services.parse_service.usecases.parse_tracks_usecase import ParseTracksUseCase


router = APIRouter()
usecase = ParseTracksUseCase()
logger = logging.getLogger(__name__)


def _run_force_parse() -> None:
    """Run heavy parse task in background so admin request returns quickly."""
    try:
        usecase.execute_parse()
    except Exception:
        logger.exception("Forced parse failed")


@router.get("/api/v1/status")
def status(
    track_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List parse status rows for admin monitoring with optional ID filter."""
    return {
        "items": usecase.list_track_status(track_id=track_id, limit=limit, offset=offset),
    }


@router.post("/api/v1/force_parse")
def force_parse():
    """Trigger asynchronous parse run for the current discovery feed."""
    health_report = usecase.health()
    if health_report["status"] != "healthy":
        return JSONResponse(status_code=503, content=health_report)

    Thread(target=_run_force_parse, daemon=True).start()
    return {"message": "parsing started"}


@router.post("/api/v1/parse/{track_id}")
def parse_single(track_id: str):
    """Trigger parsing for one track via ID."""
    health_report = usecase.health()
    if health_report["status"] != "healthy":
        return JSONResponse(status_code=503, content=health_report)

    try:
        bundle = usecase.execute_single(track_id)
        return {"message": "track parsed", "track": bundle}
    except Exception as exc:
        logger.exception("Single-track parse failed for track_id=%s", track_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
