"""
agents/intel_agent.py — Agent 1: Company Intel
Searches web + extracts round structure JSON.

FIX 4:  Uses get_llm() / get_search_client() lazy getters (not module-level singletons).
FIX 6:  async def + await llm.ainvoke().
FIX 14: Graceful fallback when Tavily returns 0 results.
FIX 15: Retry loop (3 attempts, exponential back-off 1 / 2 / 4 s) for LLM + parse errors.
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from backend.tools.web_search import search
from backend.tools.llm import get_llm
from backend.utils.parser import extract_json
from backend.graph.state import PrepState

logger = logging.getLogger(__name__)

INTEL_PROMPT = """You are an interview intelligence analyst.
Given these raw interview experience snippets for {company} ({role} role):
---
{snippets}
---
Extract and return ONLY a JSON object:
{{
  "company": "{company}", "role": "{role}",
  "rounds": [{{"name":"...","type":"oa|coding|dsa|system_design|hr|managerial",
    "confirmed_problems":["..."],"topics":["..."],"difficulty":"easy|medium|hard",
    "elimination_rate":"high|medium|low","notes":"..."}}],
  "overall_difficulty": "easy|medium|hard",
  "top_topics": ["topic1","topic2","topic3"]
}}
Return ONLY the JSON. No explanation."""

# FIX 14: fallback prompt used when Tavily returns no results
INTEL_FALLBACK_PROMPT = """You are an interview intelligence analyst.
No live interview experience data was available for {company} ({role} role).
Based on your training knowledge, generate a plausible and realistic interview
structure JSON for this company and role.
Return ONLY a JSON object:
{{
  "company": "{company}", "role": "{role}",
  "rounds": [{{"name":"...","type":"oa|coding|dsa|system_design|hr|managerial",
    "confirmed_problems":["..."],"topics":["..."],"difficulty":"easy|medium|hard",
    "elimination_rate":"high|medium|low","notes":"..."}}],
  "overall_difficulty": "easy|medium|hard",
  "top_topics": ["topic1","topic2","topic3"]
}}
Return ONLY the JSON. No explanation."""


async def intel_agent(state: PrepState) -> PrepState:
    company, role = state["company"], state["role"]
    llm = get_llm()

    # --- web search (FIX 6: search is now async) ---
    queries = [
        f"{company} {role} interview experience leetcode discuss",
        f"{company} coding interview questions geeksforgeeks",
        f"{company} software engineer interview rounds glassdoor",
    ]
    seen_urls: set[str] = set()
    snippets: list[str] = []
    for q in queries:
        try:
            results = await search(q, max_results=4)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    snippets.append(f"[{r['title']}]\n{r['content'][:600]}")
        except Exception as exc:
            logger.warning("intel_agent: search failed for query %r: %s", q, exc)

    # FIX 14: fallback when no snippets were retrieved
    if len(snippets) == 0:
        logger.warning(
            "intel_agent: no search results for %s/%s — using fallback knowledge prompt", company, role
        )
        prompt_template = INTEL_FALLBACK_PROMPT
        raw_snippets = ""
    else:
        prompt_template = INTEL_PROMPT
        raw_snippets = "\n\n".join(snippets[:10])

    prompt = prompt_template.format(company=company, role=role, snippets=raw_snippets)

    # FIX 15: retry loop (3 attempts, exponential back-off)
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            intel = extract_json(response.content)
            return {**state, "intel": intel}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)  # 1s, 2s
                logger.warning("intel_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait)
                await asyncio.sleep(wait)

    raise RuntimeError(f"intel_agent failed after 3 attempts. Last error: {last_exc}") from last_exc