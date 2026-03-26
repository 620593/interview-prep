"""
agents/schedule_agent.py — Agent 3: Schedule Builder (parallel branch 1)

Strategy: ask the LLM for ONE representative daily schedule (≤ 800 tokens output),
then expand it programmatically to fill every day in the plan.
This guarantees valid JSON regardless of timeline length and keeps TPM well under
the 6K free-tier limit.
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from backend.src.tools.llm import get_schedule_llm
from backend.src.utils.parser import extract_json
from backend.src.graph.state import PrepState

logger = logging.getLogger(__name__)

# Ask for a SINGLE-DAY template only — we expand it for all days in Python
SCHEDULE_PROMPT = """Create a standard daily schedule template for an interview prep day.
Role: {role}

Fixed time blocks:
6:00 AM  — 3h  — Learn (read/study the day's topic)
9:00 AM  — 4h  — Solve (main LeetCode problems)
1:00 PM  — 1h  — Break
2:00 PM  — 4h  — Review (backup problems + notes)
7:00 PM  — 2h  — Revision (spaced repetition flashcards)

Return ONLY this JSON for exactly ONE day (no markdown):
{{"day":1,"theme":"<topic>","slots":[{{"time":"6:00 AM","duration_min":180,"activity":"Learn","detail":"Study <topic> fundamentals","type":"learn"}},{{"time":"9:00 AM","duration_min":240,"activity":"Solve","detail":"Main LeetCode problems","type":"solve"}},{{"time":"1:00 PM","duration_min":60,"activity":"Break","detail":"Rest and recharge","type":"break"}},{{"time":"2:00 PM","duration_min":240,"activity":"Review","detail":"Backup problems and review notes","type":"review"}},{{"time":"7:00 PM","duration_min":120,"activity":"Revision","detail":"Spaced repetition","type":"review"}}]}}"""

MOCK_DAY_SLOTS = [
    {"time": "9:00 AM", "duration_min": 180, "activity": "Mock Interview",
     "detail": "Full mock coding interview (90 min) + debrief", "type": "mock"},
    {"time": "12:00 PM", "duration_min": 60, "activity": "Break", "detail": "Lunch break", "type": "break"},
    {"time": "1:00 PM", "duration_min": 60, "activity": "Weak-Area Drill",
     "detail": "Focus on hardest topics from the week", "type": "solve"},
    {"time": "2:00 PM", "duration_min": 240, "activity": "Full Revision",
     "detail": "Go through all notes, patterns, and key problems", "type": "review"},
    {"time": "6:00 PM", "duration_min": 120, "activity": "Mental Prep",
     "detail": "Relaxation, confidence building, sleep early", "type": "break"},
]


def _expand_schedule(template_day: dict, curriculum: dict, timeline_days: int) -> dict:
    """
    Given one template day from the LLM, build a full schedule for every day
    by substituting the correct topic from the curriculum.
    The final day is always a mock interview day.
    """
    days_data = curriculum.get("days", [])
    topic_by_day: dict[int, str] = {d["day"]: d.get("topic", "Review") for d in days_data}

    base_slots = template_day.get("slots", [])
    schedule = []
    for day_num in range(1, timeline_days + 1):
        topic = topic_by_day.get(day_num, "Review & Practice")
        is_last = (day_num == timeline_days)

        if is_last:
            slots = MOCK_DAY_SLOTS
            theme = "Mock Interview & Final Revision"
        else:
            slots = [
                {**slot, "detail": slot["detail"].replace("<topic>", topic)}
                for slot in base_slots
            ]
            theme = topic

        schedule.append({"day": day_num, "theme": theme, "slots": slots})

    return {"schedule": schedule}


async def schedule_agent(state: PrepState) -> PrepState:
    llm = get_schedule_llm()
    prompt = SCHEDULE_PROMPT.format(role=state["role"])

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            template_day = extract_json(response.content)
            # Expand the single template to cover the full timeline
            schedule = _expand_schedule(template_day, state["curriculum"], state["timeline_days"])
            return {**state, "schedule": schedule}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)
                logger.warning(
                    "schedule_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait
                )
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"schedule_agent failed after 3 attempts. Last error: {last_exc}"
    ) from last_exc
