"""
agents/schedule_agent.py — Agent 3: Schedule Builder (parallel branch 1)

FIX 4:  Uses get_llm() lazy getter.
FIX 6:  async def + await llm.ainvoke().
FIX 15: Retry loop (3 attempts, exponential back-off 1 / 2 / 4 s).
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from backend.tools.llm import get_llm
from backend.utils.parser import extract_json
from backend.graph.state import PrepState

logger = logging.getLogger(__name__)

SCHEDULE_PROMPT = """Build a daily hourly schedule for this curriculum: {curriculum}
Rules: 6AM-10PM, morning=learn, 9AM-1PM=solve, 1-2PM=break, 2-6PM=backup+review, 7-9PM=spaced repetition
Last day: mock interview 9AM, revision 2-6PM
Return ONLY: {{"schedule":[{{"day":1,"theme":"...","slots":[{{"time":"6:00 AM","duration_min":60,
"activity":"...","detail":"...","type":"learn|solve|review|break|mock"}}]}}]}}
Return ONLY the JSON."""


async def schedule_agent(state: PrepState) -> PrepState:
    llm = get_llm()
    prompt = SCHEDULE_PROMPT.format(curriculum=state["curriculum"])

    # FIX 15: retry loop (3 attempts, exponential back-off)
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            schedule = extract_json(response.content)
            return {**state, "schedule": schedule}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)  # 1s, 2s
                logger.warning(
                    "schedule_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"schedule_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc