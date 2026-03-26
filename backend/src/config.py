"""
config.py — Single source of truth for all environment variables.
All modules import from here; no os.getenv scattered around.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve to <project-root>/.env regardless of CWD
# Path: backend/src/config.py → parent = backend/src → parent = backend → parent = project root
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    # Groq — default model used by the startup smoke-test
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Per-agent model assignment — spread load across separate rate-limit buckets
    groq_model_intel:      str = "llama-3.3-70b-versatile"   # heavy reasoning
    groq_model_curriculum: str = "llama-3.1-8b-instant"      # fast, large JSON output
    groq_model_schedule:   str = "llama-3.1-8b-instant"      # parallel branch 1
    groq_model_pattern:    str = "llama-3.1-8b-instant"      # parallel branch 2

    # Tavily web search
    tavily_api_key: str

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "interview_prep"

    # Email — optional, used by notifier
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""


settings = Settings()
