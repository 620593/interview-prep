"""
tools/web_search.py — Tavily search wrapper.
Returns a list of {title, url, content} dicts.
Used by intel_agent to scrape interview experiences.

FIX 3: Lazy initialization via @lru_cache so TavilyClient is created on first use,
        not at import time — prevents crash when TAVILY_API_KEY is absent at startup.
FIX 7: TavilyClient.search() is synchronous/blocking.  The public `search` coroutine
        wraps it with asyncio.to_thread() so it never blocks the event loop.
"""
import asyncio
from functools import lru_cache
from tavily import TavilyClient
from src.config import settings


@lru_cache(maxsize=1)
def get_search_client() -> TavilyClient:
    """Return the shared (cached) TavilyClient.  Created on first call."""
    return TavilyClient(api_key=settings.tavily_api_key)


async def search(query: str, max_results: int = 6) -> list[dict]:
    """Async wrapper around the blocking TavilyClient.search call (FIX 7)."""
    client = get_search_client()
    # run_in_executor / asyncio.to_thread keeps the event loop unblocked
    resp = await asyncio.to_thread(
        lambda: client.search(query, max_results=max_results, search_depth="advanced")
    )
    return [
        {"title": r["title"], "url": r["url"], "content": r["content"]}
        for r in resp.get("results", [])
    ]
