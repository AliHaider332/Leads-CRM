from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
)

from app.schemas.user import UserCreate

from app.services.auth import login_user

from app.services.user import create_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# LOGIN
# POST /auth/login
# ============================================================

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    return login_user(
        login_data=login_data,
        db=db,
    )


# ============================================================
# REGISTER
# POST /auth/register
# ============================================================

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Convert RegisterRequest -> UserCreate
    # --------------------------------------------------------

    create_data = UserCreate(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        phone=user_data.phone,
        company=user_data.company,
    )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = create_user(
        user_data=create_data,
        db=db,
    )

    # --------------------------------------------------------
    # Create token immediately after registration
    # --------------------------------------------------------

    from app.core.security import create_access_token

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    # --------------------------------------------------------
    # Return frontend contract
    # --------------------------------------------------------

    return {
        "success": True,
        "token": access_token,
        "user": user,
    }