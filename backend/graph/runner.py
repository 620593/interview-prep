"""
graph/runner.py — Entry point to run the prep pipeline.

FIX 9: After ainvoke, validate that html_output is present; raise a descriptive
        RuntimeError rather than letting the router trip over a None value.
"""
import re
from backend.graph.graph import prep_graph
from backend.graph.state import PrepState


def _parse_query(query: str) -> tuple[str, str, int]:
    days_match = re.search(r"(\d+)\s*day", query, re.IGNORECASE)
    days = int(days_match.group(1)) if days_match else 7
    role_pattern = r"(AI Engineer|Backend Engineer|Software Engineer|SDE|Data Scientist|ML Engineer|Full Stack)"
    role_match = re.search(role_pattern, query, re.IGNORECASE)
    role = role_match.group(1) if role_match else "Software Engineer"
    company_match = re.search(r"\bfor\s+([A-Z][a-zA-Z0-9]+)", query)
    company = company_match.group(1) if company_match else "Unknown Company"
    return company, role, days


async def run_prep(query: str) -> PrepState:
    company, role, days = _parse_query(query)
    initial_state: PrepState = {
        "query": query, "company": company, "role": role,
        "timeline_days": days, "intel": None, "curriculum": None,
        "schedule": None, "patterns": None, "html_output": None,
        "session_id": None, "user_progress": {},
    }
    final_state = await prep_graph.ainvoke(initial_state)

    # FIX 9: validate critical keys before returning to the router
    missing = [k for k in ("html_output", "session_id", "company", "role") if not final_state.get(k)]
    if missing:
        raise RuntimeError(
            f"Pipeline completed but the following required keys are missing or None "
            f"in final_state: {missing}.  Check agent logs above for the root cause."
        )

    return final_state