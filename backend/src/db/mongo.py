"""
db/mongo.py — Motor async MongoDB client and CRUD helpers.
The client is created lazily via get_db() so it binds to uvicorn's running event loop.
"""
import logging
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.src.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_client() -> AsyncIOMotorClient:
    """Return the shared Motor client. Created on first call."""
    return AsyncIOMotorClient(settings.mongo_uri)


def get_db() -> AsyncIOMotorDatabase:
    """Return the database handle backed by the cached Motor client."""
    return _get_client()[settings.mongo_db]


def _col():
    """Shortcut to the prep_sessions collection."""
    return get_db()["prep_sessions"]


async def save_session(session_id: str, state: dict) -> None:
    await _col().update_one(
        {"session_id": session_id},
        {"$set": {
            "session_id":    session_id,
            "company":       state.get("company"),
            "role":          state.get("role"),
            "timeline_days": state.get("timeline_days"),
            "intel":         state.get("intel"),
            "curriculum":    state.get("curriculum"),
            "schedule":      state.get("schedule"),
            "patterns":      state.get("patterns"),
            "html_output":   state.get("html_output"),
            "user_progress": state.get("user_progress", {}),
        }},
        upsert=True,
    )


async def get_session(session_id: str) -> dict | None:
    return await _col().find_one({"session_id": session_id}, {"_id": 0})


async def update_progress(session_id: str, progress: dict) -> bool:
    result = await _col().update_one(
        {"session_id": session_id}, {"$set": {"user_progress": progress}}
    )
    return result.matched_count > 0
