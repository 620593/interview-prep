"""
tools/llm.py — Single Groq LLaMA client shared across all agents.
Call get_llm() to obtain the cached instance.

FIX 2: Lazy initialization via @lru_cache so ChatGroq is created on first use,
        not at import time — prevents crash when GROQ_API_KEY is absent at startup.
"""
from functools import lru_cache
from langchain_groq import ChatGroq
from backend.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Return the shared (cached) ChatGroq client.  Created on first call."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.3,
        max_tokens=8192,  # 120B models are more verbose — 4096 caused truncated JSON
    )