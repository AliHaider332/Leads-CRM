from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class LeadStatus(str, Enum):
    NEW = "New"
    QUALIFIED = "Qualified"
    PROPOSAL = "Proposal"
    WON = "Won"
    LOST = "Lost"


class LeadPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Lead(Base):
    __tablename__ = "leads"

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

    company = Column(
        String(150),
        nullable=True,
    )

    status = Column(
        SQLEnum(
            LeadStatus,
            name="leadstatus",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=LeadStatus.NEW,
    )

    priority = Column(
        SQLEnum(
            LeadPriority,
            name="leadpriority",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=LeadPriority.MEDIUM,
    )

    source = Column(
        String(50),
        nullable=True,
    )

    value = Column(
        Float,
        nullable=False,
        default=0,
    )

    tags = Column(
        JSON,
        nullable=False,
        default=list,
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
    )

    ai_summary = Column(
        Text,
        nullable=True,
    )

    ai_risk_score = Column(
        Float,
        nullable=True,
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
        back_populates="leads",
    )

    notes =Column(
        Text,
        nullable=True,
    )

    tasks = relationship(
        "Task",
        back_populates="related_lead",
        cascade="all, delete-orphan",
    )