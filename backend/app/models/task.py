from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Task(Base):
    __tablename__ = "tasks"

    # Primary Key
    _id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Task Information
    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
        default="",
    )

    # Task Dates
    due_date = Column(
        DateTime,
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    # Task Status
    status = Column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
    )

    # Task Priority
    priority = Column(
        SQLEnum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM,
    )

    # Related Lead
    related_lead_id = Column(
        Integer,
        ForeignKey("leads._id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Related Contact - Optional
    related_contact_id = Column(
        Integer,
        ForeignKey("contacts._id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Created At
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Relationships
    related_lead = relationship(
        "Lead",
        back_populates="tasks",
    )

    related_contact = relationship(
        "Contact",
        back_populates="tasks",
    )
