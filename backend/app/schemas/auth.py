from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


# ============================================================
# LOGIN
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# REGISTER
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None
    company: str = "Self Startup"


# ============================================================
# AUTH RESPONSE
# ============================================================

class AuthResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse


