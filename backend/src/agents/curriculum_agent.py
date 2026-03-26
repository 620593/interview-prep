"""
agents/curriculum_agent.py — Agent 2: Curriculum Design

Receives company intel and designs a structured day-by-day study curriculum.
Intel is slimmed to key fields only to stay within free-tier TPM limits.
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.tools.llm import get_curriculum_llm
from src.utils.parser import extract_json
from src.graph.state import PrepState

logger = logging.getLogger(__name__)

CURRICULUM_PROMPT = """You are an expert interview coach. Design a {days}-day study curriculum.

Company: {company} | Role: {role}
Difficulty: {difficulty} | Top topics: {top_topics}
High-elimination rounds: {hard_rounds}

Rules:
- Topics with high elimination_rate go in the first half
- Each day: exactly 3 main + 2 backup problems
- Last day: mock interview + revision only
- Problem balance: 60% medium, 25% hard, 15% easy

Return ONLY this JSON (no explanation, no markdown):
{{"total_days":{days},"days":[{{"day":1,"topic":"...","subtopics":["..."],"priority":"critical|high|medium","goal":"...","problems":[{{"name":"...","difficulty":"easy|medium|hard","pattern":"...","leetcode_id":1,"type":"main|backup"}}]}}]}}"""


def _slim_intel(intel: dict) -> dict:
    """Extract only the fields the curriculum prompt needs — keeps token count low."""
    rounds = intel.get("rounds", [])
    hard_rounds = [
        r.get("name", "") for r in rounds if r.get("elimination_rate") == "high"
    ]
    return {
        "company": intel.get("company", ""),
        "difficulty": intel.get("overall_difficulty", "medium"),
        "top_topics": ", ".join(intel.get("top_topics", [])[:8]),
        "hard_rounds": ", ".join(hard_rounds) or "none",
    }


async def curriculum_agent(state: PrepState) -> PrepState:
    llm = get_curriculum_llm()
    slim = _slim_intel(state["intel"])
    prompt = CURRICULUM_PROMPT.format(
        days=state["timeline_days"],
        role=state["role"],
        **slim,
    )

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            curriculum = extract_json(response.content)
            return {**state, "curriculum": curriculum}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)
                logger.warning(
                    "curriculum_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"curriculum_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc
