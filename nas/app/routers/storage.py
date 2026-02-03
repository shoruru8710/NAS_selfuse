"""Storage router: commit, download, delete."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service_token import require_service_token
from app.dependencies import get_db
from app.schemas.storage import CommitResponse
from app.services.storage import delete_object, get_object, store_file

router = APIRouter(dependencies=[Depends(require_service_token)])


@router.post("/commit", response_model=CommitResponse)
async def commit_file(
    file: UploadFile,
    mime: str = "application/octet-stream",
    sha256: str = "",
    size: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Receive file from EC2 and store permanently."""
    result = await store_file(
        db=db,
        file=file,
        original_filename=file.filename or "unknown",
        mime_type=mime,
        sha256=sha256,
        size_bytes=size,
    )
    return result


@router.get("/download/{object_id}")
async def download_file(
    object_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Stream file back to EC2."""
    obj = await get_object(db, object_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return FileResponse(
        path=obj.storage_path,
        media_type=obj.mime_type,
        filename=obj.original_filename,
    )


@router.delete("/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stored_object(
    object_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete object from storage."""
    deleted = await delete_object(db, object_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
