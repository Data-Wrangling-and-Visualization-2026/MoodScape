from fastapi import APIRouter
import asyncio


router = APIRouter()

@router.get("/health")
async def check_health():
    return {
        "service" : "LLM",
        "status" : "healthy"
    }
