"""Storage service: UUID-based file storage on NAS filesystem."""

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.storage import StoredObject


def _make_storage_path(object_id: uuid.UUID) -> Path:
    """Generate storage path with 2-level directory hashing.

    Example: /data/storage/objects/ab/cd/<uuid>.bin
    """
    hex_id = object_id.hex
    return Path(settings.storage_root) / hex_id[:2] / hex_id[2:4] / f"{object_id}.bin"


async def store_file(
    db: AsyncSession,
    file: UploadFile,
    original_filename: str,
    mime_type: str,
    sha256: str,
    size_bytes: int,
) -> dict:
    """Store uploaded file and create DB record."""
    object_id = uuid.uuid4()
    storage_path = _make_storage_path(object_id)

    # Create directories
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file to disk
    actual_size = 0
    async with aiofiles.open(storage_path, "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)
            actual_size += len(chunk)

    # Create DB record
    stored_obj = StoredObject(
        id=object_id,
        original_filename=original_filename,
        mime_type=mime_type,
        size_bytes=actual_size,
        sha256=sha256,
        storage_path=str(storage_path),
    )
    db.add(stored_obj)
    await db.commit()

    return {"object_id": object_id, "stored_bytes": actual_size}


async def get_object(db: AsyncSession, object_id: uuid.UUID) -> StoredObject | None:
    """Get stored object by ID."""
    result = await db.execute(select(StoredObject).where(StoredObject.id == object_id))
    return result.scalar_one_or_none()


async def delete_object(db: AsyncSession, object_id: uuid.UUID) -> bool:
    """Delete stored object from DB and filesystem."""
    obj = await get_object(db, object_id)
    if not obj:
        return False

    # Remove from filesystem
    try:
        if os.path.exists(obj.storage_path):
            os.remove(obj.storage_path)
    except OSError:
        pass

    await db.delete(obj)
    await db.commit()
    return True
