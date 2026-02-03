"""RAG pipeline: extract -> chunk -> embed -> store."""

import logging
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.storage import StoredObject
from app.schemas.rag import SearchResultItem, SnippetResult

from .chunker import chunk_text
from .embedder import embed_texts
from .extractor import extract_text
from .vector_store import delete_by_file_id, search_similar, store_chunks

logger = logging.getLogger(__name__)


async def index_file(db: AsyncSession, file_id: str) -> int:
    """Full indexing pipeline for a file.

    1. Find stored object
    2. Extract text
    3. Chunk
    4. Generate embeddings
    5. Store in pgvector

    Returns number of chunks created.
    """
    # Find the stored object
    result = await db.execute(
        select(StoredObject).where(StoredObject.id == file_id)
    )
    stored_obj = result.scalar_one_or_none()
    if not stored_obj:
        logger.warning(f"StoredObject not found for file_id={file_id}")
        return 0

    # Delete existing chunks
    await delete_by_file_id(db, file_id)

    # Extract text
    text = extract_text(stored_obj.storage_path, stored_obj.mime_type)
    if not text.strip():
        logger.info(f"No text extracted from {file_id}")
        return 0

    # Chunk
    chunks = chunk_text(text)
    if not chunks:
        return 0

    # Generate embeddings
    embeddings = embed_texts(chunks)

    # Store
    chunk_records = [
        {
            "file_id": file_id,
            "owner_id": "",  # Set by EC2 when needed
            "visibility": "private",
            "chunk_index": i,
            "content": chunk,
            "source_hint": f"chunk {i + 1}/{len(chunks)}",
            "embedding": embedding,
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    count = await store_chunks(db, chunk_records)
    logger.info(f"Indexed {count} chunks for file_id={file_id}")
    return count


async def search_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 20,
) -> list[SearchResultItem]:
    """Search for relevant chunks.

    1. Embed query
    2. Vector search
    3. Group by file_id
    """
    query_embedding = embed_texts([query])[0]
    raw_results = await search_similar(db, query_embedding, top_k=top_k)

    # Group by file_id
    grouped: dict[str, list] = defaultdict(list)
    scores: dict[str, float] = {}

    for r in raw_results:
        file_id = r["file_id"]
        grouped[file_id].append(
            SnippetResult(
                chunk_id=r["chunk_id"],
                text_excerpt=r["content"][:500],
                source_hint=r["source_hint"],
            )
        )
        # Keep highest score per file
        if file_id not in scores or r["score"] > scores[file_id]:
            scores[file_id] = r["score"]

    return [
        SearchResultItem(
            file_id=file_id,
            score=scores[file_id],
            snippets=snippets,
        )
        for file_id, snippets in grouped.items()
    ]


async def delete_file_chunks(db: AsyncSession, file_id: str) -> int:
    """Delete all chunks for a file."""
    return await delete_by_file_id(db, file_id)
