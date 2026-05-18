from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "browser_agent"

    # Collections
    TASKS_COLLECTION: str = "tasks"
    SESSIONS_COLLECTION: str = "sessions"
    RESULTS_COLLECTION: str = "results"

    # LLM (Groq)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # Browser
    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT_MS: int = 30000
    BROWSER_KEEP_OPEN_SECONDS: int = 0

    # Agent
    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
