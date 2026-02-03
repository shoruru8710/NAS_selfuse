"""pgvector operations for storing and querying embeddings."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rag import DocumentChunk


async def store_chunks(
    db: AsyncSession,
    chunks: list[dict],
) -> int:
    """Store document chunks with embeddings.

    Args:
        db: DB session
        chunks: List of dicts with keys:
            file_id, owner_id, visibility, chunk_index, content, source_hint, embedding

    Returns:
        Number of chunks stored
    """
    for chunk_data in chunks:
        chunk = DocumentChunk(
            id=uuid.uuid4(),
            file_id=chunk_data["file_id"],
            owner_id=chunk_data.get("owner_id", ""),
            visibility=chunk_data.get("visibility", "private"),
            chunk_index=chunk_data["chunk_index"],
            content=chunk_data["content"],
            source_hint=chunk_data.get("source_hint", ""),
            embedding=chunk_data.get("embedding"),
        )
        db.add(chunk)

    await db.commit()
    return len(chunks)


async def search_similar(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int = 20,
) -> list[dict]:
    """Find similar chunks using pgvector cosine distance.

    Returns list of dicts with file_id, chunk_id, score, content, source_hint.
    """
    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.file_id,
            DocumentChunk.content,
            DocumentChunk.source_hint,
            DocumentChunk.chunk_index,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .order_by("distance")
        .limit(top_k)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "chunk_id": str(row.id),
            "file_id": row.file_id,
            "content": row.content,
            "source_hint": row.source_hint,
            "score": 1.0 - row.distance,  # Convert distance to similarity
        }
        for row in rows
    ]


async def delete_by_file_id(db: AsyncSession, file_id: str) -> int:
    """Delete all chunks for a given file_id."""
    result = await db.execute(
        delete(DocumentChunk).where(DocumentChunk.file_id == file_id)
    )
    await db.commit()
    return result.rowcount
