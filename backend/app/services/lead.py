from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


# ============================================================
# CREATE
# ============================================================

def create_lead(
    lead_data: LeadCreate,
    current_user_id: int,
    db: Session,
):
    """
    Create a new lead for the authenticated user.
    """

    lead = Lead(
        owner_id=current_user_id,

        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,

        status=lead_data.status.capitalize(),
        priority=lead_data.priority.capitalize(),
        source=lead_data.source,

        value=lead_data.value,

        notes=lead_data.notes,
        tags=lead_data.tags,

        # Backend-managed fields
        sort_order=0,
        ai_summary="",
        ai_risk_score=None,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


# ============================================================
# GET ALL
# ============================================================

def get_leads(
    db: Session,
    owner_id: int,
    status: str | None = None,
    priority: str | None = None,
    source: str | None = None,
    search: str | None = None,
):
    """
    Get only the leads belonging to the authenticated user.
    """

    query = db.query(Lead).filter(
        Lead.owner_id == owner_id
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if status:
        query = query.filter(
            Lead.status == status
        )

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    if priority:
        query = query.filter(
            Lead.priority == priority
        )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    if source:
        query = query.filter(
            Lead.source.ilike(f"%{source}%")
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Lead.name.ilike(search_pattern),
                Lead.email.ilike(search_pattern),
                Lead.company.ilike(search_pattern),
                Lead.phone.ilike(search_pattern),
            )
        )

    # --------------------------------------------------------
    # Ordering
    # --------------------------------------------------------

    return (
        query
        .order_by(Lead.sort_order.asc())
        .all()
    )


# ============================================================
# GET SINGLE
# ============================================================

def get_lead_by_id(
    db: Session,
    lead_id: int,
    owner_id: int,
):
    """
    Get one lead.

    IMPORTANT:
    owner_id ensures a user cannot access
    another user's lead.
    """

    return (
        db.query(Lead)
        .filter(
            Lead._id == lead_id,
            Lead.owner_id == owner_id,
        )
        .first()
    )


# ============================================================
# UPDATE
# ============================================================

def update_lead(
    db: Session,
    lead_id: int,
    owner_id: int,
    lead_data: LeadUpdate,
):
    """
    Partially update a lead.
    """

    # --------------------------------------------------------
    # Find user's lead
    # --------------------------------------------------------

    lead = (
        db.query(Lead)
        .filter(
            Lead._id == lead_id,
            Lead.owner_id == owner_id,
        )
        .first()
    )

    if not lead:
        return None

    # --------------------------------------------------------
    # Only fields actually sent by frontend
    # --------------------------------------------------------

    update_data = lead_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Frontend uses "order"
    # Database uses "sort_order"
    # --------------------------------------------------------

    if "order" in update_data:
        update_data["sort_order"] = update_data.pop("order")

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            lead,
            field,
            value,
        )

    db.commit()
    db.refresh(lead)

    return lead


# ============================================================
# DELETE
# ============================================================

def delete_lead(
    db: Session,
    lead_id: int,
    owner_id: int,
):
    """
    Delete a lead belonging to the authenticated user.
    """

    lead = (
        db.query(Lead)
        .filter(
            Lead._id == lead_id,
            Lead.owner_id == owner_id,
        )
        .first()
    )

    if not lead:
        return False

    db.delete(lead)
    db.commit()

    return True


# ============================================================
# REORDER
# ============================================================

def reorder_leads(
    db: Session,
    owner_id: int,
    updates,
):
    """
    Update status and order for multiple leads.

    Frontend sends:

    {
        "updates": [
            {
                "id": 1,
                "status": "Qualified",
                "order": 0
            },
            {
                "id": 2,
                "status": "Won",
                "order": 1
            }
        ]
    }
    """

    for update in updates:

        lead = (
            db.query(Lead)
            .filter(
                Lead._id == update.id,
                Lead.owner_id == owner_id,
            )
            .first()
        )

        # Ignore IDs that don't belong to this user
        if not lead:
            continue

        lead.status = update.status
        lead.sort_order = update.order

    db.commit()

    return {
        "success": True,
        "message": "Pipeline updated",
    }