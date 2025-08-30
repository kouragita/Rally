from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    PROJECT_NAME: str = "Climate Wildlife AI Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./data/app.db" # Changed database path
    
    # Service API Keys & Settings
    INFLECTION_AI_API_KEY: str | None = None
    INFLECTION_AI_BASE_URL: str = "https://api.inflection.ai"
    INFLECTION_AI_MODEL: str = "Pi-3.1"
    NOAA_API_KEY: str | None = None
    NASA_API_KEY: str | None = None

settings = Settings()