from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    _id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
        index=True,
    )

    title = Column(
        String(100),
        nullable=True,
    )

    company = Column(
        String(150),
        nullable=True,
        index=True,
    )

    email = Column(
        String(255),
        nullable=False,
        index=True,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    tags = Column(
        JSON,
        nullable=False,
        default=list,
    )

    favorite = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner = relationship(
        "User",
        back_populates="contacts",
    )

    notes = relationship(
        "Note",
        back_populates="contact",
    )

    tasks = relationship(
        "Task",
        back_populates="related_contact",
    )