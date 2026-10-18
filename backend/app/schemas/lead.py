from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# Base
# ============================================================

class LeadBase(BaseModel):
    name: str
    email: EmailStr

    phone: str | None = None
    company: str | None = None

    status: str = "New"
    priority: str = "Medium"
    source: str | None = None

    value: float = 0

    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


# ============================================================
# Create
# ============================================================

class LeadCreate(LeadBase):
    pass


# ============================================================
# Update
# ============================================================

class LeadUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

    phone: str | None = None
    company: str | None = None

    status: str | None = None
    priority: str | None = None
    source: str | None = None

    value: float | None = None

    notes: str | None = None
    tags: list[str] = Field(default_factory=list) 

    order: int | None = None

    ai_summary: str | None = None
    ai_risk_score: float | None = None


# ============================================================
# Response
# ============================================================

class LeadResponse(BaseModel):
    """
    Converts SQLAlchemy fields into the exact frontend format.

    Database:
        _id
        sort_order
        ai_summary
        ai_risk_score
        created_at
        updated_at

    Frontend:
        _id
        order
        aiSummary
        aiRiskScore
        createdAt
        updatedAt
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    # SQLAlchemy: _id
    # Frontend: _id
    id: int = Field(
        validation_alias="_id",
        serialization_alias="_id",
    )

    name: str
    email: EmailStr

    phone: str | None = None
    company: str | None = None

    status: str
    priority: str
    source: str | None = None

    value: float

    notes: str | None = None
    tags: list[str] = Field(default_factory=list)

    # SQLAlchemy: sort_order
    # Frontend: order
    order: int = Field(
        validation_alias="sort_order",
        serialization_alias="order",
    )

    # SQLAlchemy: ai_summary
    # Frontend: aiSummary
    ai_summary: str | None = Field(
        default=None,
        serialization_alias="aiSummary",
    )

    # SQLAlchemy: ai_risk_score
    # Frontend: aiRiskScore
    ai_risk_score: float | None = Field(
        default=None,
        serialization_alias="aiRiskScore",
    )

    # SQLAlchemy: created_at
    # Frontend: createdAt
    created_at: datetime = Field(
        serialization_alias="createdAt",
    )

    # SQLAlchemy: updated_at
    # Frontend: updatedAt
    updated_at: datetime = Field(
        serialization_alias="updatedAt",
    )


# ============================================================
# Response wrappers
# ============================================================

class LeadResponseWrapper(BaseModel):
    """
    Used by:
        GET /leads/{id}
        POST /leads
        PATCH /leads/{id}

    Frontend expects:

    {
        "success": true,
        "lead": {...}
    }
    """

    success: bool
    lead: LeadResponse


class LeadListResponse(BaseModel):
    """
    Used by:

        GET /leads

    Frontend expects:

    {
        "success": true,
        "count": 10,
        "leads": [...]
    }
    """

    success: bool
    count: int
    leads: list[LeadResponse]


class LeadMessageResponse(BaseModel):
    """
    Used by:

        DELETE /leads/{id}
        PATCH /leads/reorder
    """

    success: bool
    message: str


# ============================================================
# Reorder
# ============================================================

class LeadReorderItem(BaseModel):
    id: int
    status: str
    order: int


class LeadReorderRequest(BaseModel):
    updates: list[LeadReorderItem]