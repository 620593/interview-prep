"""
agents/pattern_agent.py — Agent 4: Pattern Library (parallel branch 2)

Runs in parallel with schedule_agent. Sends only a flat list of unique topic names
to stay well within the free-tier TPM limits.
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.tools.llm import get_pattern_llm
from src.utils.parser import extract_json
from src.graph.state import PrepState

logger = logging.getLogger(__name__)

PATTERN_PROMPT = """Generate algorithm pattern cheat sheets.
Company: {company} | Role: {role}
Topics: {topics}

Return ONLY this JSON (no markdown, no explanation):
{{"patterns":[{{"topic":"...","template":"...","key_insight":"...","time_complexity":"O(...)","space_complexity":"O(...)","company_tip":"...","common_mistakes":["..."],"problems":["..."]}}]}}
Include every topic listed above."""


def _extract_topics(curriculum: dict, limit: int = 15) -> list[str]:
    """Return unique topics from the curriculum, capped at `limit`."""
    seen: set[str] = set()
    topics: list[str] = []
    for day in curriculum.get("days", []):
        t = day.get("topic", "")
        if t and t not in seen:
            seen.add(t)
            topics.append(t)
            if len(topics) >= limit:
                break
    return topics


async def pattern_agent(state: PrepState) -> PrepState:
    llm = get_pattern_llm()
    topics = _extract_topics(state["curriculum"])
    prompt = PATTERN_PROMPT.format(
        company=state["company"],
        role=state["role"],
        topics=", ".join(topics),
    )

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            patterns = extract_json(response.content)
            return {**state, "patterns": patterns}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)
                logger.warning(
                    "pattern_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"pattern_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc
