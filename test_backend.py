"""
test_backend.py — Offline structural tests (no API keys needed).

Tests:
  1. All module imports resolve
  2. PrepState shape is correct
  3. extract_json handles all LLM response formats
  4. Graph nodes are wired correctly
  5. Query parser extracts company/role/days

Run: uv run python test_backend.py
"""
import sys, os
from collections.abc import Callable, Mapping
from typing import Any, cast
sys.path.insert(0, os.path.dirname(__file__))

# ── Patch config before import so missing .env doesn't crash ──────────────
from unittest.mock import patch
os.environ.setdefault("GROQ_API_KEY",   "test-key")
os.environ.setdefault("TAVILY_API_KEY", "test-key")
os.environ.setdefault("MONGO_URI",      "mongodb://localhost:27017")

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
results: list[bool] = []

def test(name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
        print(f"  {PASS} {name}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {name}")
        print(f"      → {e}")
        results.append(False)


print("\n── 1. Import Tests ───────────────────────────────────────────")

def t_import_state():
    from backend.graph.state import PrepState
    assert isinstance(PrepState.__annotations__, dict)
    assert "intel" in PrepState.__annotations__

def t_import_parser():
    from backend.utils.parser import extract_json
    assert callable(extract_json)

def t_import_runner():
    from backend.graph.runner import parse_query
    assert callable(parse_query)

def t_import_agents():
    # Agents import LLM/search clients — mock them
    with patch("backend.tools.llm.ChatGroq"), \
         patch("backend.tools.web_search.TavilyClient"):
        from backend.agents.intel_agent      import intel_agent     # noqa
        from backend.agents.curriculum_agent import curriculum_agent # noqa
        from backend.agents.schedule_agent   import schedule_agent   # noqa
        from backend.agents.pattern_agent    import pattern_agent    # noqa
        from backend.agents.renderer_agent   import renderer_agent   # noqa
        assert all([
            callable(intel_agent),
            callable(curriculum_agent),
            callable(schedule_agent),
            callable(pattern_agent),
            callable(renderer_agent),
        ])

test("PrepState imports", t_import_state)
test("extract_json imports", t_import_parser)
test("runner.parse_query imports", t_import_runner)
test("All 5 agents import", t_import_agents)


print("\n── 2. PrepState Shape ────────────────────────────────────────")

def t_state_keys():
    from backend.graph.state import PrepState
    required = {"query","company","role","timeline_days",
                "intel","curriculum","schedule","patterns",
                "html_output","session_id","user_progress"}
    assert required == set(PrepState.__annotations__.keys()), \
        f"Missing keys: {required - set(PrepState.__annotations__.keys())}"

test("PrepState has all 11 required keys", t_state_keys)


print("\n── 3. Parser Tests ───────────────────────────────────────────")

def t_parser_plain_json():
    from backend.utils.parser import extract_json
    result = extract_json('{"company": "Gridlex", "rounds": []}')
    assert isinstance(result, dict)
    result = cast(dict[str, Any], result)
    assert result["company"] == "Gridlex"

def t_parser_fenced_json():
    from backend.utils.parser import extract_json
    result = extract_json('```json\n{"company": "Gridlex"}\n```')
    assert isinstance(result, dict)
    result = cast(dict[str, Any], result)
    assert result["company"] == "Gridlex"

def t_parser_json_in_prose():
    from backend.utils.parser import extract_json
    result = extract_json('Here is the result:\n{"company": "Gridlex"}\nDone.')
    assert isinstance(result, dict)
    result = cast(dict[str, Any], result)
    assert result["company"] == "Gridlex"

def t_parser_list():
    from backend.utils.parser import extract_json
    result = extract_json('```json\n[1, 2, 3]\n```')
    assert result == [1, 2, 3]

def t_parser_raises_on_garbage():
    from backend.utils.parser import extract_json
    try:
        extract_json("no json here at all")
        assert False, "Should have raised"
    except ValueError:
        pass  # expected

test("Plain JSON", t_parser_plain_json)
test("Fenced ```json block", t_parser_fenced_json)
test("JSON embedded in prose", t_parser_json_in_prose)
test("JSON array", t_parser_list)
test("Raises ValueError on garbage input", t_parser_raises_on_garbage)


print("\n── 4. Query Parser Tests ─────────────────────────────────────")

def t_query_full():
    from backend.graph.runner import parse_query
    c, r, d = parse_query("Prepare me for Gridlex AI Engineer interview in 7 days")
    assert c == "Gridlex", f"company={c}"
    assert r == "AI Engineer", f"role={r}"
    assert d == 7, f"days={d}"

def t_query_default_days():
    from backend.graph.runner import parse_query
    _, _, d = parse_query("Prepare me for Amazon interview")
    assert d == 7  # default

def t_query_sde():
    from backend.graph.runner import parse_query
    c, r, d = parse_query("Get me ready for Zepto SDE interview in 14 days")
    assert c == "Zepto"
    assert r == "SDE"
    assert d == 14

test("Full query: company + role + days", t_query_full)
test("Missing days → defaults to 7", t_query_default_days)
test("SDE role + 14 days", t_query_sde)


print("\n── 5. Graph Structure Tests ──────────────────────────────────")

def t_graph_builds():
    with patch("backend.tools.llm.ChatGroq"), \
         patch("backend.tools.web_search.TavilyClient"):
        from backend.graph.graph import build_graph
        g = build_graph()
        assert g is not None

def t_graph_has_all_nodes():
    with patch("backend.tools.llm.ChatGroq"), \
         patch("backend.tools.web_search.TavilyClient"):
        from backend.graph.graph import build_graph
        g = build_graph()
        # LangGraph compiled graph exposes nodes via get_graph()
        graph_repr = cast(Any, g).get_graph()
        node_names = set(cast(Mapping[str, Any], graph_repr.nodes).keys())
        expected = {"intel", "curriculum", "schedule", "patterns", "synthesis", "renderer"}
        assert expected.issubset(node_names), \
            f"Missing nodes: {expected - node_names}"

test("Graph compiles without error", t_graph_builds)
test("All 6 nodes present in graph", t_graph_has_all_nodes)


# ── Summary ───────────────────────────────────────────────────────────────
passed = sum(results)
total  = len(results)
color  = "\033[92m" if passed == total else "\033[93m"
print(f"\n{color}{'─'*50}\033[0m")
print(f"{color}  {passed}/{total} tests passed\033[0m")
print(f"{color}{'─'*50}\033[0m\n")

if passed < total:
    sys.exit(1)