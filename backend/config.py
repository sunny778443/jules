import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Fallback to local SQLite file 'jarvis.db' to guarantee 100% uptime and offline execution support
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///jarvis.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jarvis_ultra_secure_secret_signing_key_998811")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
