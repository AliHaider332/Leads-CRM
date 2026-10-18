from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserUpdate,
)


# ============================================================
# CREATE USER / REGISTER
# ============================================================

def create_user(
    user_data: UserCreate,
    db: Session,
):
    # --------------------------------------------------------
    # Check existing email
    # --------------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = User(
        name=user_data.name,
        email=user_data.email,

        password_hash=hash_password(
            user_data.password
        ),

        phone=user_data.phone,
        company=user_data.company,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# GET USER
# ============================================================

def get_user(
    user_id: int,
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ============================================================
# UPDATE USER
# ============================================================

def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # --------------------------------------------------------
    # Only fields sent by frontend
    # --------------------------------------------------------

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # If email is being changed, make sure it isn't taken
    # --------------------------------------------------------

    if "email" in update_data:

        existing_user = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != user_id,
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------
  
    for field, value in update_data.items():
        setattr(
            user,
            field,
            value,
        )

    db.commit()
    db.refresh(user)

    return user