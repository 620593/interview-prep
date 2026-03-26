"""
agents/renderer_agent.py — Agent 5: HTML Renderer via Jinja2.
Converts the fully assembled pipeline state into a rendered HTML tracker page.
"""
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.graph.state import PrepState

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=False,
)


async def renderer_agent(state: PrepState) -> PrepState:
    session_id = state.get("session_id") or str(uuid.uuid4())[:8]
    template = _env.get_template("tracker.html.j2")
    html = template.render(
        company=state["company"], role=state["role"],
        timeline_days=state["timeline_days"], intel=state["intel"],
        curriculum=state["curriculum"], schedule=state["schedule"],
        patterns=state["patterns"], session_id=session_id,
    )
    return {**state, "html_output": html, "session_id": session_id}
