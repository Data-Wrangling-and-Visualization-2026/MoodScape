from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PARSER_URL: str = "http://localhost:8001"
    BD_URL: str = "http://localhost:8000"
    PARSER_TIMEOUT: int = 30

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    TEMPERATURE: float = 0.3

    model_config = SettingsConfigDict(env_file="config.env")

settings = Settings()