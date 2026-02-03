"""RAG router: index, search, reindex, delete."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service_token import require_service_token
from app.dependencies import get_db
from app.schemas.rag import RAGSearchRequest, RAGSearchResponse
from app.services.rag.pipeline import delete_file_chunks, index_file, search_chunks

router = APIRouter(dependencies=[Depends(require_service_token)])


@router.post("/index/{file_id}")
async def index_file_endpoint(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Index a file for RAG search."""
    result = await index_file(db, file_id)
    return {"status": "indexed", "chunks": result}


@router.get("/search", response_model=RAGSearchResponse)
async def search_endpoint(
    q: str,
    top_k: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Vector search across document chunks."""
    results = await search_chunks(db, query=q, top_k=top_k)
    return RAGSearchResponse(results=results)


@router.post("/reindex")
async def reindex_endpoint(
    file_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Reindex a specific file or all files."""
    # TODO: Implement full reindex logic
    if file_id:
        await delete_file_chunks(db, file_id)
        result = await index_file(db, file_id)
        return {"status": "reindexed", "file_id": file_id, "chunks": result}
    return {"status": "full_reindex_not_implemented"}


@router.delete("/index/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_index_endpoint(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete RAG index for a file."""
    await delete_file_chunks(db, file_id)
