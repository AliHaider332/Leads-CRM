from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.lead import Lead

from app.schemas.ai import (
    AIStatusResponse,
    LeadSummaryRequest,
    LeadSummaryResponse,
    GenerateEmailRequest,
    GenerateEmailResponse,
    SalesInsightsRequest,
    SalesInsightsResponse,
)

from app.services.grok import ask_grok


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ============================================================
# AI STATUS
# GET /ai/status
# ============================================================

@router.get(
    "/status",
    response_model=AIStatusResponse,
)
def ai_status(
    current_user: User = Depends(get_current_user),
):
    return {
        "success": True,
        "configured": bool(settings.GROK_KEY),
        "model": settings.GROK_MODEL,
    }


# ============================================================
# LEAD SUMMARY
# POST /ai/lead-summary
# ============================================================

@router.post(
    "/lead-summary",
    response_model=LeadSummaryResponse,
)
def lead_summary(
    data: LeadSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead._id == data.lead_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    status = (
        lead.status.value
        if hasattr(lead.status, "value")
        else str(lead.status)
    )

    priority = (
        lead.priority.value
        if hasattr(lead.priority, "value")
        else str(lead.priority)
    )

    prompt = f"""
Analyze this CRM lead and provide a concise sales assessment.

Lead information:

Name: {lead.name}
Email: {lead.email}
Company: {lead.company}
Status: {status}
Priority: {priority}
Value: {lead.value}

Return EXACTLY this format:

SUMMARY:
<2-4 sentence summary>

RISK_SCORE:
<number from 0 to 100>

SUGGESTED_PRIORITY:
<Low, Medium, or High>

NEXT_BEST_ACTION:
<one specific action the salesperson should take>

Do not add anything outside this format.
"""

    try:
        result = ask_grok(
            system_prompt=(
                "You are an AI sales assistant inside a CRM. "
                "Analyze leads objectively and provide concise, "
                "practical sales guidance."
            ),
            user_prompt=prompt,
        )

        summary = ""
        risk_score = 50
        suggested_priority = priority
        next_best_action = ""

        if "SUMMARY:" in result:
            summary_part = result.split("SUMMARY:", 1)[1]

            if "RISK_SCORE:" in summary_part:
                summary = summary_part.split(
                    "RISK_SCORE:",
                    1,
                )[0].strip()

        if "RISK_SCORE:" in result:
            risk_part = result.split("RISK_SCORE:", 1)[1]

            if "SUGGESTED_PRIORITY:" in risk_part:
                risk_value = risk_part.split(
                    "SUGGESTED_PRIORITY:",
                    1,
                )[0].strip()

                try:
                    risk_score = int(
                        "".join(
                            c for c in risk_value
                            if c.isdigit()
                        )
                    )
                except ValueError:
                    risk_score = 50

        if "SUGGESTED_PRIORITY:" in result:
            priority_part = result.split(
                "SUGGESTED_PRIORITY:",
                1,
            )[1]

            if "NEXT_BEST_ACTION:" in priority_part:
                suggested_priority = priority_part.split(
                    "NEXT_BEST_ACTION:",
                    1,
                )[0].strip()

        if "NEXT_BEST_ACTION:" in result:
            next_best_action = result.split(
                "NEXT_BEST_ACTION:",
                1,
            )[1].strip()

        return {
            "success": True,
            "summary": summary or result,
            "riskScore": max(0, min(100, risk_score)),
            "suggestedPriority": suggested_priority,
            "nextBestAction": next_best_action,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI summarization failed: {str(e)}",
        )


# ============================================================
# GENERATE EMAIL
# POST /ai/generate-email
# ============================================================

@router.post(
    "/generate-email",
    response_model=GenerateEmailResponse,
)
def generate_email(
    data: GenerateEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead._id == data.lead_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    status = (
        lead.status.value
        if hasattr(lead.status, "value")
        else str(lead.status)
    )

    priority = (
        lead.priority.value
        if hasattr(lead.priority, "value")
        else str(lead.priority)
    )

    prompt = f"""
Generate a professional sales email for this CRM lead.

Lead:
Name: {lead.name}
Email: {lead.email}
Company: {lead.company}
Status: {status}
Priority: {priority}
Value: {lead.value}

Purpose:
{data.purpose}

Tone:
{data.tone}

Return EXACTLY:

SUBJECT:
<email subject>

BODY:
<email body>

Do not add explanations outside this format.
"""

    try:
        result = ask_grok(
            system_prompt=(
                "You are an AI email writing assistant "
                "inside a professional CRM."
            ),
            user_prompt=prompt,
        )

        subject = ""
        body = result

        if "SUBJECT:" in result and "BODY:" in result:
            subject_part, body_part = result.split(
                "BODY:",
                1,
            )

            subject = subject_part.replace(
                "SUBJECT:",
                "",
            ).strip()

            body = body_part.strip()

        return {
            "success": True,
            "subject": subject,
            "body": body,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email generation failed: {str(e)}",
        )


# ============================================================
# SALES INSIGHTS
# POST /ai/sales-insights
# ============================================================

@router.post(
    "/sales-insights",
    response_model=SalesInsightsResponse,
)
def sales_insights(
    data: SalesInsightsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leads = (
        db.query(Lead)
        .filter(
            Lead.owner_id == current_user.id,
        )
        .all()
    )

    if not leads:
        return {
            "success": True,
            "headline": "There are no leads to analyze yet.",
            "insights": [
                "Your CRM currently has no leads.",
            ],
            "recommendations": [
                "Add leads to your CRM before generating sales insights.",
            ],
            "healthScore": 0,
        }

    lead_data = []

    for lead in leads:
        status = (
            lead.status.value
            if hasattr(lead.status, "value")
            else str(lead.status)
        )

        priority = (
            lead.priority.value
            if hasattr(lead.priority, "value")
            else str(lead.priority)
        )

        lead_data.append({
            "name": lead.name,
            "company": lead.company,
            "status": status,
            "priority": priority,
            "value": lead.value or 0,
        })

    prompt = f"""
Analyze the following CRM sales pipeline.

Analysis period:
{data.period}

Leads:
{lead_data}

Provide useful and objective sales insights.

Return EXACTLY:

HEADLINE:
<one sentence summarizing overall pipeline health>

INSIGHTS:
- insight 1
- insight 2
- insight 3

RECOMMENDATIONS:
- recommendation 1
- recommendation 2
- recommendation 3

HEALTH_SCORE:
<number from 0 to 100>

Do not add anything outside this format.
"""

    try:
        result = ask_grok(
            system_prompt=(
                "You are an AI sales analyst inside a CRM. "
                "Analyze CRM data objectively and provide "
                "actionable recommendations."
            ),
            user_prompt=prompt,
        )

        headline = ""
        insights = []
        recommendations = []
        health_score = 50

        # -------------------------
        # Headline
        # -------------------------

        if "HEADLINE:" in result:
            headline_part = result.split(
                "HEADLINE:",
                1,
            )[1]

            if "INSIGHTS:" in headline_part:
                headline = headline_part.split(
                    "INSIGHTS:",
                    1,
                )[0].strip()

        # -------------------------
        # Insights
        # -------------------------

        if "INSIGHTS:" in result:
            insights_part = result.split(
                "INSIGHTS:",
                1,
            )[1]

            if "RECOMMENDATIONS:" in insights_part:
                insights_part = insights_part.split(
                    "RECOMMENDATIONS:",
                    1,
                )[0]

            insights = [
                line.strip().lstrip("-").strip()
                for line in insights_part.splitlines()
                if line.strip()
            ]

        # -------------------------
        # Recommendations
        # -------------------------

        if "RECOMMENDATIONS:" in result:
            recommendations_part = result.split(
                "RECOMMENDATIONS:",
                1,
            )[1]

            if "HEALTH_SCORE:" in recommendations_part:
                recommendations_part = recommendations_part.split(
                    "HEALTH_SCORE:",
                    1,
                )[0]

            recommendations = [
                line.strip().lstrip("-").strip()
                for line in recommendations_part.splitlines()
                if line.strip()
            ]

        # -------------------------
        # Health score
        # -------------------------

        if "HEALTH_SCORE:" in result:
            health_part = result.split(
                "HEALTH_SCORE:",
                1,
            )[1].strip()

            try:
                health_score = int(
                    "".join(
                        c for c in health_part
                        if c.isdigit()
                    )
                )
            except ValueError:
                health_score = 50

        return {
            "success": True,
            "headline": headline or "Pipeline analysis completed.",
            "insights": insights,
            "recommendations": recommendations,
            "healthScore": max(0, min(100, health_score)),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sales insights generation failed: {str(e)}",
        )