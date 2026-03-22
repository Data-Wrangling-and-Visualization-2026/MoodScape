from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PARSER_URL: str = "http://parse_service_app:8001"
    BD_URL: str = "http://bd_service_app:8000"
    PARSER_TIMEOUT: int = 30

    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    TEMPERATURE: float = 0.3

    model_config = SettingsConfigDict(env_file="config.env")

settings = Settings()