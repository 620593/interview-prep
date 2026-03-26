"""
routers/progress.py — PATCH /progress/{session_id}, GET /progress/{session_id}
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db.mongo import update_progress, get_session

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressUpdate(BaseModel):
    progress: dict[str, bool]


@router.patch("/{session_id}")
async def save_progress(session_id: str, body: ProgressUpdate):
    updated = await update_progress(session_id, body.progress)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "saved"}


@router.get("/{session_id}")
async def load_progress(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"progress": session.get("user_progress", {})}
