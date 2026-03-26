"""
tools/llm.py — Per-agent Groq LLM factory.

Each agent gets a dedicated cached model instance to distribute API load
across separate rate-limit buckets, eliminating 429 errors during parallel execution.

Agent → Model mapping (configurable via env vars in config.py):
  intel      → llama-3.3-70b-versatile   reasoning + web-data synthesis
  curriculum → llama-3.1-8b-instant      fast, large JSON output
  schedule   → llama-3.1-8b-instant      parallel branch 1
  pattern    → llama-3.1-8b-instant      parallel branch 2
"""
from functools import lru_cache
from langchain_groq import ChatGroq
from src.config import settings


def _make(model: str, temperature: float = 0.3, max_tokens: int = 8192) -> ChatGroq:
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Default getter — used by startup smoke-test and tests."""
    return _make(settings.groq_model)


@lru_cache(maxsize=1)
def get_intel_llm() -> ChatGroq:
    return _make(settings.groq_model_intel, temperature=0.2, max_tokens=4096)


@lru_cache(maxsize=1)
def get_curriculum_llm() -> ChatGroq:
    return _make(settings.groq_model_curriculum, temperature=0.2, max_tokens=8000)


@lru_cache(maxsize=1)
def get_schedule_llm() -> ChatGroq:
    # max_tokens kept low: input + output must stay under 6K free-tier TPM
    return _make(settings.groq_model_schedule, temperature=0.2, max_tokens=2000)


@lru_cache(maxsize=1)
def get_pattern_llm() -> ChatGroq:
    # max_tokens kept low: input + output must stay under 6K free-tier TPM
    return _make(settings.groq_model_pattern, temperature=0.2, max_tokens=2000)
