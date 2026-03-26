"""
agents/pattern_agent.py — Agent 4: Pattern Library (parallel branch 2)

FIX 4:  Uses get_llm() lazy getter.
FIX 6:  async def + await llm.ainvoke().
FIX 15: Retry loop (3 attempts, exponential back-off 1 / 2 / 4 s).
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from backend.src.tools.llm import get_llm
from backend.src.utils.parser import extract_json
from backend.src.graph.state import PrepState

logger = logging.getLogger(__name__)

PATTERN_PROMPT = """Generate pattern cheat sheets for: Company={company}, Role={role}, Topics={topics}
Return ONLY: {{"patterns":[{{"topic":"...","template":"...","key_insight":"...","time_complexity":"O(...)",
"space_complexity":"O(...)","company_tip":"...","common_mistakes":["..."],"problems":["..."]}}]}}
Include ALL topics. Return ONLY the JSON."""


def _extract_topics(curriculum: dict) -> list[str]:
    seen: set[str] = set()
    topics: list[str] = []
    for day in curriculum.get("days", []):
        t = day.get("topic", "")
        if t and t not in seen:
            seen.add(t)
            topics.append(t)
    return topics


async def pattern_agent(state: PrepState) -> PrepState:
    llm = get_llm()
    topics = _extract_topics(state["curriculum"])
    prompt = PATTERN_PROMPT.format(
        company=state["company"], role=state["role"], topics=", ".join(topics)
    )

    # FIX 15: retry loop (3 attempts, exponential back-off)
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            patterns = extract_json(response.content)
            return {**state, "patterns": patterns}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)  # 1s, 2s
                logger.warning(
                    "pattern_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"pattern_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc
