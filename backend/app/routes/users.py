from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.security import get_current_user

from app.models.user import User

from app.schemas.user import UserUpdate,MeResponse

from app.services.user import update_user


router = APIRouter(
    prefix="/auth",
    tags=["User Profile"],
)


# ============================================================
# GET CURRENT USER
#
# GET /auth/me
# ============================================================

@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
)
def get_current_user_route(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "success": True,
        "user": current_user,
    }


# ============================================================
# UPDATE PROFILE
#
# PUT /auth/profile
# ============================================================

@router.put(
    "/profile",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    user = update_user(
        user_id=current_user.id,
        user_data=user_data,
        db=db,
    )

    return {
        "success": True,
        "user": user,
    }