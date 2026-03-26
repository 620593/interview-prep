"""
graph/state.py — PrepState is the shared memory of the entire pipeline.

All keys carry a `last_wins` reducer because agents in parallel branches return
{**state, "their_key": ...}, which makes LangGraph see concurrent writes to every
key in the dict. Without a reducer on ALL keys, LangGraph raises InvalidUpdateError
for any key touched by more than one concurrent writer.
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
    # Written by parallel branches — reducer prevents InvalidUpdateError
    schedule:      Annotated[Optional[dict], last_wins]
    patterns:      Annotated[Optional[dict], last_wins]
    html_output:   Annotated[Optional[str],  last_wins]
    session_id:    Annotated[Optional[str],  last_wins]
    user_progress: Annotated[Optional[dict], last_wins]
