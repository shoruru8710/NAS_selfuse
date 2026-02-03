"""Embedding generation (local sentence-transformers or OpenAI)."""

import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_local_model():
    """Load sentence-transformers model (cached)."""
    from sentence_transformers import SentenceTransformer

    logger.info(f"Loading embedding model: {settings.embedding_model}")
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Uses local model or OpenAI based on settings.embedding_provider.
    """
    if not texts:
        return []

    if settings.embedding_provider == "openai":
        return _embed_openai(texts)

    return _embed_local(texts)


def _embed_local(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using local sentence-transformers model."""
    model = _get_local_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def _embed_openai(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using OpenAI API."""
    try:
        import openai

        client = openai.OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small",
        )
        return [item.embedding for item in response.data]
    except ImportError:
        logger.error("openai package not installed")
        raise
