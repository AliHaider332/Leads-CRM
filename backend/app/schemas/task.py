from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = ""
    due_date: datetime
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    related_lead_id: int
    related_contact_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    related_lead_id: int | None = None
    related_contact_id: int | None = None