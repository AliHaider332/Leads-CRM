from datetime import datetime

from pydantic import BaseModel


class AnalyticsStats(BaseModel):
    revenueWon: float
    pipelineValue: float
    totalLeads: int
    totalContacts: int
    openTasks: int
    conversionRate: int


class PipelineStage(BaseModel):
    stage: str
    count: int
    value: float


class TrendItem(BaseModel):
    month: str
    leads: int
    won: float


class RecentLead(BaseModel):
    id: int
    name: str
    company: str | None
    status: str
    value: float
    updatedAt: datetime


class AnalyticsOverviewResponse(BaseModel):
    success: bool
    stats: AnalyticsStats
    pipeline: list[PipelineStage]
    trend: list[TrendItem]
    recentLeads: list[RecentLead]