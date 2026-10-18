from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# CREATE USER
# ============================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None
    company: str = "Self Startup"


# ============================================================
# UPDATE USER
# ============================================================

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    avatar: str | None = None
    password: str | None = None


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str

    email: EmailStr

    phone: str | None = None

    role: str

    company: str

    avatar: str | None = None

    created_at: datetime = Field(
        serialization_alias="createdAt",
    )



class MeResponse(BaseModel):
    success: bool
    user: UserResponse




class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str