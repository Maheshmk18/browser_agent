from __future__ import annotations

import asyncio
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


async def embed_text(text: str) -> list[float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_embeddings().embed_query, text)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_embeddings().embed_documents, texts)
