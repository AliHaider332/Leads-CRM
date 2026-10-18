from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
)

from app.models.user import User

from app.schemas.auth import LoginRequest


# ============================================================
# LOGIN USER
# ============================================================

def login_user(
    login_data: LoginRequest,
    db: Session,
):
    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == login_data.email
        )
        .first()
    )

    # --------------------------------------------------------
    # User doesn't exist
    # --------------------------------------------------------

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    password_valid = verify_password(
        login_data.password,
        user.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Create JWT
    # --------------------------------------------------------

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # Return exactly what frontend expects:
    #
    # {
    #   success: true,
    #   token: "...",
    #   user: {...}
    # }
    # --------------------------------------------------------

    return {
        "success": True,
        "token": access_token,
        "user": user,
    }