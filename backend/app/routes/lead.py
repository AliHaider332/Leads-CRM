from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User

from app.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadMessageResponse,
    LeadReorderRequest,
    LeadResponseWrapper,
    LeadUpdate,
)

from app.services.lead import (
    create_lead,
    delete_lead,
    get_lead_by_id,
    get_leads,
    reorder_leads,
    update_lead,
)


router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


# ============================================================
# CREATE
# POST /leads
# ============================================================

@router.post(
    "",
    response_model=LeadResponseWrapper,
    status_code=status.HTTP_201_CREATED,
)
def create_lead_route(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = create_lead(
        lead_data=lead_data,
        current_user_id=current_user.id,
        db=db,
    )

    return {
        "success": True,
        "lead": lead,
    }


# ============================================================
# GET ALL
# GET /leads
# ============================================================

@router.get(
    "",
    response_model=LeadListResponse,
    status_code=status.HTTP_200_OK,
)
def get_leads_endpoint(
    status: str | None = Query(
        default=None,
    ),
    priority: str | None = Query(
        default=None,
    ),
    source: str | None = Query(
        default=None,
    ),
    search: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leads = get_leads(
        db=db,
        owner_id=current_user.id,
        status=status,
        priority=priority,
        source=source,
        search=search,
    )

    return {
        "success": True,
        "count": len(leads),
        "leads": leads,
    }


# ============================================================
# REORDER
#
# IMPORTANT:
# This route MUST be before /{id}
#
# PATCH /leads/reorder
# ============================================================

@router.patch(
    "/reorder",
    response_model=LeadMessageResponse,
    status_code=status.HTTP_200_OK,
)
def reorder_leads_endpoint(
    data: LeadReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = reorder_leads(
        db=db,
        owner_id=current_user.id,
        updates=data.updates,
    )

    return result


# ============================================================
# GET SINGLE
# GET /leads/{id}
# ============================================================

@router.get(
    "/{id}",
    response_model=LeadResponseWrapper,
    status_code=status.HTTP_200_OK,
)
def get_single_lead(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = get_lead_by_id(
        db=db,
        lead_id=id,
        owner_id=current_user.id,
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return {
        "success": True,
        "lead": lead,
    }


# ============================================================
# UPDATE
# PATCH /leads/{id}
# ============================================================

@router.put(
    "/{id}",
    response_model=LeadResponseWrapper,
    status_code=status.HTTP_200_OK,
)
def update_lead_endpoint(
    id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = update_lead(
        db=db,
        lead_id=id,
        owner_id=current_user.id,
        lead_data=lead_data,
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return {
        "success": True,
        "lead": lead,
    }


# ============================================================
# DELETE
# DELETE /leads/{id}
# ============================================================

@router.delete(
    "/{id}",
    response_model=LeadMessageResponse,
    status_code=status.HTTP_200_OK,
)
def delete_lead_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_lead(
        db=db,
        lead_id=id,
        owner_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return {
        "success": True,
        "message": "Lead deleted",
    }