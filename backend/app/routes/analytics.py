from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.database import get_db

from app.models.user import User
from app.models.lead import Lead
from app.models.contact import Contact
from app.models.task import Task

from app.schemas.analytics import AnalyticsOverviewResponse


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
)
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # Get user's leads
    # ---------------------------------------------------------

    leads = (
        db.query(Lead)
        .filter(
            Lead.owner_id == current_user.id
        )
        .all()
    )

    # ---------------------------------------------------------
    # Get user's contacts
    # ---------------------------------------------------------

    contacts = (
        db.query(Contact)
        .filter(
            Contact.owner_id == current_user.id
        )
        .all()
    )

    # ---------------------------------------------------------
    # Pipeline
    # ---------------------------------------------------------

    stages = [
        "New",
        "Qualified",
        "Proposal",
        "Won",
        "Lost",
    ]

    by_stage = {
        stage: {
            "count": 0,
            "value": 0,
        }
        for stage in stages
    }

    total_value = 0
    won_value = 0

    for lead in leads:
        status = (
            lead.status.value
            if hasattr(lead.status, "value")
            else str(lead.status)
        )

        value = lead.value or 0

        if status not in by_stage:
            by_stage[status] = {
                "count": 0,
                "value": 0,
            }

        by_stage[status]["count"] += 1
        by_stage[status]["value"] += value

        total_value += value

        if status == "Won":
            won_value += value

    # ---------------------------------------------------------
    # Conversion rate
    # ---------------------------------------------------------

    won = by_stage.get("Won", {}).get("count", 0)
    lost = by_stage.get("Lost", {}).get("count", 0)

    closed = won + lost

    conversion_rate = (
        round((won / closed) * 100)
        if closed
        else 0
    )

    # ---------------------------------------------------------
    # Last 6 months trend
    # ---------------------------------------------------------

    labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    now = datetime.utcnow()

    months = []

    for i in range(5, -1, -1):
        year = now.year
        month = now.month - i

        while month <= 0:
            month += 12
            year -= 1

        months.append({
            "year": year,
            "month": month,
            "key": f"{year}-{month}",
            "label": labels[month - 1],
        })

    month_index = {
        month["key"]: index
        for index, month in enumerate(months)
    }

    trend = [
        {
            "month": month["label"],
            "leads": 0,
            "won": 0,
        }
        for month in months
    ]

    for lead in leads:
        if not lead.created_at:
            continue

        created = lead.created_at

        key = f"{created.year}-{created.month}"

        if key in month_index:
            index = month_index[key]

            trend[index]["leads"] += 1

            status = (
                lead.status.value
                if hasattr(lead.status, "value")
                else str(lead.status)
            )

            if status == "Won":
                trend[index]["won"] += lead.value or 0

    # ---------------------------------------------------------
    # Recent leads
    # ---------------------------------------------------------

    recent_leads = (
        sorted(
            leads,
            key=lambda lead: lead.updated_at or lead.created_at,
            reverse=True,
        )[:6]
    )

    recent_leads_response = []

    for lead in recent_leads:
        status = (
            lead.status.value
            if hasattr(lead.status, "value")
            else str(lead.status)
        )

        recent_leads_response.append({
            "id": lead._id,
            "name": lead.name,
            "company": lead.company,
            "status": status,
            "value": lead.value or 0,
            "updatedAt": lead.updated_at,
        })

    # ---------------------------------------------------------
    # Open tasks
    # ---------------------------------------------------------

    open_tasks = (
        db.query(Task)
        .join(Lead)
        .filter(
            Lead.owner_id == current_user.id,
            Task.status != "Completed",
        )
        .count()
    )

    # ---------------------------------------------------------
    # Pipeline response
    # ---------------------------------------------------------

    pipeline = [
        {
            "stage": stage,
            "count": by_stage[stage]["count"],
            "value": by_stage[stage]["value"],
        }
        for stage in stages
    ]

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------

    return {
        "success": True,

        "stats": {
            "revenueWon": won_value,
            "pipelineValue": total_value,
            "totalLeads": len(leads),
            "totalContacts": len(contacts),
            "openTasks": open_tasks,
            "conversionRate": conversion_rate,
        },

        "pipeline": pipeline,

        "trend": trend,

        "recentLeads": recent_leads_response,
    }