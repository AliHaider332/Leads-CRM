from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    contact_id: int | None = None
    pinned: bool = False


class NoteUpdate(BaseModel):
    content: str | None = Field(None, min_length=1)
    contact_id: int | None = None
    pinned: bool | None = None


class NoteResponse(BaseModel):
    _id: int
    content: str
    contact_id: int | None
    pinned: bool
    createdAt: datetime