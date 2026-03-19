import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.services.parse_service.api.admin_controller import router as admin_router, usecase
from backend.services.parse_service.api.internal_controller import router as internal_router
from backend.services.parse_service.infrastructure.scheduler import SchedulerService


scheduler = SchedulerService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Start/stop background scheduler around app lifecycle."""
    scheduler_enabled = (
        os.getenv("PARSE_SCHEDULER_ENABLED", "false").strip().lower() == "true"
    )

    if scheduler_enabled:
        parse_interval_minutes = int(os.getenv("PARSE_INTERVAL_MINUTES", "5"))
        scheduler.add_job(usecase.execute_parse, minutes=parse_interval_minutes)
        lyrics_interval_minutes = int(os.getenv("LYRICS_INTERVAL_MINUTES", "10"))
        scheduler.add_job(usecase.execute_lyrics_backfill, minutes=lyrics_interval_minutes)
        scheduler.start()

    yield

    if scheduler_enabled:
        scheduler.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(admin_router)
app.include_router(internal_router)

@app.get("/health")
def health():
    """Expose service health and return `503` when dependencies are unavailable."""
    report = usecase.health()
    if report["status"] != "healthy":
        return JSONResponse(status_code=503, content=report)
    return report
