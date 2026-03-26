"""
routers/prep.py — POST /prep/generate, GET /prep/{session_id}
"""
import traceback
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from backend.src.graph.runner import run_prep
from backend.src.db.mongo import save_session, get_session

router = APIRouter(prefix="/prep", tags=["prep"])
logger = logging.getLogger(__name__)


class PrepRequest(BaseModel):
    query: str


class PrepResponse(BaseModel):
    # str_max_length=None allows html_output which can be 50–200 KB
    model_config = ConfigDict(str_max_length=None)

    session_id:    str
    company:       str
    role:          str
    timeline_days: int
    html_output:   str


@router.post("/generate", response_model=PrepResponse)
async def generate_prep(req: PrepRequest):
    try:
        final_state = await run_prep(req.query)
        try:
            await save_session(final_state["session_id"], final_state)
        except Exception as db_err:
            logger.warning("MongoDB save failed: %s", db_err)
        return PrepResponse(
            session_id=final_state["session_id"],
            company=final_state["company"],
            role=final_state["role"],
            timeline_days=final_state["timeline_days"],
            html_output=final_state["html_output"],
        )
    except Exception:
        tb = traceback.format_exc()
        logger.error("/prep/generate failed:\n%s", tb)
        return JSONResponse(status_code=500, content={"detail": tb})


@router.get("/{session_id}")
async def get_prep(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
