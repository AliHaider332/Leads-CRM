from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="owner",
        nullable=False
    )

    company: Mapped[str] = mapped_column(
        String(100),
        default="Self Startup",
        nullable=False
    )

    avatar: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.utcnow,
    nullable=False
    )

    # Relationship with Lead
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    contacts: Mapped[list["Contact"]] = relationship(
    "Contact",
    back_populates="owner",
    cascade="all, delete-orphan",
)