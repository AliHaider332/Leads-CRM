from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    name: str = Field(..., max_length=100)
    title: str | None = Field(None, max_length=100)
    company: str | None = Field(None, max_length=150)
    email: EmailStr
    phone: str | None = Field(None, max_length=30)
    tags: list[str] = []


class ContactCreate(ContactBase):
    favorite: bool = False


class ContactUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    title: str | None = Field(None, max_length=100)
    company: str | None = Field(None, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    tags: list[str] | None = None
    favorite: bool | None = None


class ContactResponse(BaseModel):
    _id: int
    name: str
    title: str | None
    company: str | None
    email: str
    phone: str | None
    tags: list[str]
    favorite: bool
    createdAt: datetime
    updatedAt: datetime


class ContactListResponse(BaseModel):
    success: bool
    count: int
    contacts: list[ContactResponse]


class ContactSingleResponse(BaseModel):
    success: bool
    contact: ContactResponse


class ContactDeleteResponse(BaseModel):
    success: bool
    message: str