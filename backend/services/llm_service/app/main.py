from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.llm_pipeline import LlmPipeline
from contextlib import asynccontextmanager
from app.api.endpoints import router
import asyncio

pipeline = LlmPipeline()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting the llm pipeline")
    task = asyncio.create_task(pipeline.start())
    try:
        yield
    finally:
        pipeline.stop()
        task.cancel()
        logger.info("The llm service stops running")

def create_app() -> FastAPI:
    app = FastAPI(
        title="LLM service", 
        lifespan=lifespan
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/")
    async def root():
        return {
            "service" : "Llm service",
            "endpoints" : [
                "/health"
            ]
        }
    
    return app


app = create_app()