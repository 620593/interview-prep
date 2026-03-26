"""
main.py — FastAPI entry point.
Run: cd interview-prep-agent && uv run uvicorn backend.main:app --reload

FIX 12: @app.on_event("startup") validates all env vars and external connections
        so config errors are caught immediately rather than on the first request.
"""
import logging
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.routers.prep import router as prep_router
from backend.src.routers.progress import router as progress_router
from backend.src.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Interview Prep Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prep_router)
app.include_router(progress_router)


@app.on_event("startup")
async def startup_checks() -> None:
    """FIX 12: Validate env vars, LLM reachability, and DB connectivity at startup."""
    # 1 — Log loaded settings (mask secret values)
    logger.info("=== Startup configuration ===")
    logger.info("  groq_model       : %s", settings.groq_model)
    logger.info("  groq_api_key     : %s…", settings.groq_api_key[:6])
    logger.info("  tavily_api_key   : %s…", settings.tavily_api_key[:6])
    logger.info("  mongo_uri        : %s", settings.mongo_uri)
    logger.info("  mongo_db         : %s", settings.mongo_db)

    # 2 — Smoke-test the Groq API key with a tiny prompt
    try:
        from langchain_core.messages import HumanMessage
        from backend.src.tools.llm import get_llm
        llm = get_llm()
        resp = await llm.ainvoke([HumanMessage(content="Reply with OK")])
        logger.info("✅ Groq LLM reachable — reply: %s", resp.content[:40])
    except Exception:
        logger.error("❌ Groq LLM unreachable at startup:\n%s", traceback.format_exc())

    # 3 — Ping MongoDB (non-fatal)
    try:
        from backend.src.db.mongo import get_db
        db = get_db()
        await db.command("ping")
        logger.info("✅ MongoDB reachable at %s", settings.mongo_uri)
    except Exception:
        logger.warning(
            "⚠️  MongoDB unreachable at startup (non-fatal — DB writes will fail on request):\n%s",
            traceback.format_exc(),
        )


@app.get("/health")
async def health():
    return {"status": "ok"}

