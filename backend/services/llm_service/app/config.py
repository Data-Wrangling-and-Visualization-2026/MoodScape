from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PARSER_URL : str = os.getenv("PARSER_URL","")
    BD_URL : str = os.getenv("BD_URL","http://localhost:8000")
    PARSER_TIMEOUT = 30

    OLLAMA_URL : str = os.getenv("OLLAMA_URL","http://localhost:11434/v1")
    OLLAMA_MODEL : str = "llama3.1:8b"
    TEMPERATURE = 0.3
    class Config:
        env_file = ".env"

settings = Settings()