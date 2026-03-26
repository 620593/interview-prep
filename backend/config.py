"""
config.py — Single source of truth for all env vars.
All modules import from here; no os.getenv scattered around.

"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve to <project-root>/.env no matter where the server is started from
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    # LLM
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    # Search
    tavily_api_key: str

    # DB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "interview_prep"

    # Email (optional — used by notifier in v2)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""


# Singleton — import `settings` everywhere
settings = Settings()