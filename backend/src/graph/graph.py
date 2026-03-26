"""
graph/graph.py — LangGraph pipeline wiring.
Flow: intel → curriculum → [schedule ‖ patterns] → synthesis → renderer
"""
from langgraph.graph import StateGraph, END
from backend.src.graph.state import PrepState
from backend.src.agents.intel_agent import intel_agent
from backend.src.agents.curriculum_agent import curriculum_agent
from backend.src.agents.schedule_agent import schedule_agent
from backend.src.agents.pattern_agent import pattern_agent
from backend.src.agents.renderer_agent import renderer_agent


async def synthesis_node(state: PrepState) -> PrepState:
    """Gate node: waits for both parallel branches to complete before rendering."""
    assert state.get("schedule"), "schedule_agent did not populate state"
    assert state.get("patterns"), "pattern_agent did not populate state"
    return state


def build_graph() -> StateGraph:
    g = StateGraph(PrepState)
    g.add_node("intel",      intel_agent)
    g.add_node("curriculum", curriculum_agent)
    g.add_node("schedule",   schedule_agent)
    g.add_node("patterns",   pattern_agent)
    g.add_node("synthesis",  synthesis_node)
    g.add_node("renderer",   renderer_agent)
    g.set_entry_point("intel")
    g.add_edge("intel",      "curriculum")
    g.add_edge("curriculum", "schedule")
    g.add_edge("curriculum", "patterns")
    g.add_edge("schedule",   "synthesis")
    g.add_edge("patterns",   "synthesis")
    g.add_edge("synthesis",  "renderer")
    g.add_edge("renderer",   END)
    return g.compile()


prep_graph = build_graph()
