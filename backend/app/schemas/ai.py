from pydantic import BaseModel, Field, ConfigDict


class AIStatusResponse(BaseModel):
    success: bool
    configured: bool
    model: str


class LeadSummaryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lead_id: int = Field(alias="leadId")


class LeadSummaryResponse(BaseModel):
    success: bool
    summary: str
    riskScore: int
    suggestedPriority: str
    nextBestAction: str


class GenerateEmailRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lead_id: int = Field(alias="leadId")
    purpose: str = Field(..., min_length=1, max_length=500)
    tone: str = "professional"


class GenerateEmailResponse(BaseModel):
    success: bool
    subject: str
    body: str


class SalesInsightsRequest(BaseModel):
    period: str = "30d"


class SalesInsightsResponse(BaseModel):
    success: bool
    headline: str
    insights: list[str]
    recommendations: list[str]
    healthScore: int