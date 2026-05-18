from __future__ import annotations

from functools import lru_cache

from langchain_groq import ChatGroq

from config.settings import settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
    )


@lru_cache(maxsize=1)
def get_vision_llm() -> ChatGroq:
    """Vision-capable Groq model for the Vision node (screenshot analysis)."""
    return ChatGroq(
        model=settings.GROQ_VISION_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.0,
        max_tokens=1024,
    )
