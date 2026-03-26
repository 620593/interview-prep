"""
agents/curriculum_agent.py — Agent 2: Curriculum Design

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

CURRICULUM_PROMPT = """You are an expert interview coach designing a study curriculum.
Company intel: {intel}
Timeline: {days} days | Role: {role}
Rules:
1. Topics with "high" elimination_rate go in the first half
2. Each day has exactly 5 problems (3 main + 2 backup)
3. Last day is always mock interview + revision
4. Balance: 60% medium, 25% hard, 15% easy
Return ONLY this JSON:
{{"total_days":{days},"days":[{{"day":1,"topic":"...","subtopics":["..."],
"priority":"critical|high|medium","goal":"...","problems":[{{"name":"...","difficulty":"easy|medium|hard",
"pattern":"...","leetcode_id":123,"type":"main|backup"}}]}}]}}
Return ONLY the JSON."""


async def curriculum_agent(state: PrepState) -> PrepState:
    llm = get_llm()
    prompt = CURRICULUM_PROMPT.format(
        intel=state["intel"], days=state["timeline_days"], role=state["role"]
    )

    # FIX 15: retry loop (3 attempts, exponential back-off)
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            curriculum = extract_json(response.content)
            return {**state, "curriculum": curriculum}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)  # 1s, 2s
                logger.warning(
                    "curriculum_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"curriculum_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc
