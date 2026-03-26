"""
agents/intel_agent.py — Agent 1: Company Intel
Searches web + extracts round structure JSON.

Model: llama-3.3-70b-versatile (reasoning + web-data synthesis)
"""
import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.tools.web_search import search
from src.tools.llm import get_intel_llm
from src.utils.parser import extract_json
from src.graph.state import PrepState

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

INTEL_FALLBACK_PROMPT = """You are an interview intelligence analyst.
No live interview data was available for {company} ({role} role).
Based on your training knowledge, generate a realistic interview structure JSON.
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
    llm = get_intel_llm()

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

    if len(snippets) == 0:
        logger.warning(
            "intel_agent: no search results for %s/%s — using fallback prompt", company, role
        )
        prompt_template = INTEL_FALLBACK_PROMPT
        raw_snippets = ""
    else:
        prompt_template = INTEL_PROMPT
        raw_snippets = "\n\n".join(snippets[:10])

    prompt = prompt_template.format(company=company, role=role, snippets=raw_snippets)

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            intel = extract_json(response.content)
            return {**state, "intel": intel}
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = 2 ** (attempt - 1)
                logger.warning("intel_agent attempt %d failed (%s); retrying in %ds", attempt, exc, wait)
                await asyncio.sleep(wait)

    raise RuntimeError(f"intel_agent failed after 3 attempts. Last error: {last_exc}") from last_exc
