"""
graph/state.py — PrepState is the shared memory of the entire pipeline.

FIX 5 (revised): ALL keys carry a `last_wins` reducer.
Reason: agents that run in parallel branches both return {**state, "their_key": ...},
which means LangGraph sees concurrent writes to every key in the state dict —
not just the one that changed.  Without a reducer on ALL keys, LangGraph 1.1.x
raises InvalidUpdateError("Can receive only one value per step") for any key
touched by more than one concurrent writer.

The `last_wins` reducer (return b if b is not None else a) is safe here because:
  - Sequential nodes overwrite their key: clean, no conflict.
  - Parallel nodes (schedule / patterns) each only change one key but carry all
    others unchanged; last_wins keeps the first non-None value either way.
"""
from typing import Annotated, Optional, TypedDict


def last_wins(a, b):
    """Reducer: prefer the newer (b) value; fall back to existing (a) if b is None."""
    return b if b is not None else a


class PrepState(TypedDict):
    query:         Annotated[str,            last_wins]
    company:       Annotated[str,            last_wins]
    role:          Annotated[str,            last_wins]
    timeline_days: Annotated[int,            last_wins]
    intel:         Annotated[Optional[dict], last_wins]
    curriculum:    Annotated[Optional[dict], last_wins]
    # Written by parallel branches — reducer is critical here
    schedule:      Annotated[Optional[dict], last_wins]
    patterns:      Annotated[Optional[dict], last_wins]
    html_output:   Annotated[Optional[str],  last_wins]
    session_id:    Annotated[Optional[str],  last_wins]
    user_progress: Annotated[Optional[dict], last_wins]
