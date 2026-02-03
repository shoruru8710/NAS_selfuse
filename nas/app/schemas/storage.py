"""Pydantic schemas for storage endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class CommitResponse(BaseModel):
    object_id: uuid.UUID
    stored_bytes: int


class StoredObjectResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    created_at: datetime

    model_config = {"from_attributes": True}
