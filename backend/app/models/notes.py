from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    # Primary Key
    _id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Note Content
    content = Column(
        Text,
        nullable=False,
    )

    # Contact (Optional)
    contact_id = Column(
        Integer,
        ForeignKey("contacts._id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Pinned
    pinned = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )



    contact = relationship(
        "Contact",
        back_populates="notes",
    )
