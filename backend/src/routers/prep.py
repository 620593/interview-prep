"""
routers/prep.py — POST /prep/generate, GET /prep/{session_id}

FIX 10: PrepResponse carries model_config with str_max_length=None so Pydantic
        won't reject the large html_output string (50–200 KB).
        The endpoint is already async so it handles 30–90 s pipelines natively.
"""
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from backend.src.graph.runner import run_prep
from backend.src.db.mongo import save_session, get_session

router = APIRouter(prefix="/prep", tags=["prep"])


class PrepRequest(BaseModel):
    query: str


class PrepResponse(BaseModel):
    # FIX 10: no string-length cap — html_output can be 50–200 KB
    model_config = ConfigDict(str_max_length=None)

    session_id:    str
    company:       str
    role:          str
    timeline_days: int
    html_output:   str


@router.post("/generate", response_model=PrepResponse)
async def generate_prep(req: PrepRequest):
    # NOTE: pipeline takes 30–90 s; the endpoint is async so uvicorn won't stall.
    try:
        final_state = await run_prep(req.query)
        try:
            await save_session(final_state["session_id"], final_state)
        except Exception as db_err:
            print(f"[WARN] MongoDB save failed: {db_err}")
        return PrepResponse(
            session_id=final_state["session_id"],
            company=final_state["company"],
            role=final_state["role"],
            timeline_days=final_state["timeline_days"],
            html_output=final_state["html_output"],
        )
    except Exception:
        tb = traceback.format_exc()
        print(f"\n[ERROR] /prep/generate failed:\n{tb}")
        return JSONResponse(status_code=500, content={"detail": tb})


@router.get("/{session_id}")
async def get_prep(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
