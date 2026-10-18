from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.lead import Lead
from app.models.contact import Contact

from app.schemas.task import TaskCreate, TaskUpdate


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def task_response(task: Task):
    return {
        "_id": task._id,
        "title": task.title,
        "description": task.description or "",
        "dueDate": task.due_date,
        "status": task.status.value,
        "priority": task.priority.value,

        "relatedLead": (
            {
                "_id": task.related_lead._id,
                "name": task.related_lead.name,
                "email": task.related_lead.email,
                "company": task.related_lead.company,
                "status": (
                    task.related_lead.status.value
                    if hasattr(task.related_lead.status, "value")
                    else task.related_lead.status
                ),
            }
            if task.related_lead
            else None
        ),

        "relatedContact": (
            {
                "_id": task.related_contact._id,
                "name": task.related_contact.name,
                "email": task.related_contact.email,
                "company": task.related_contact.company,
            }
            if task.related_contact
            else None
        ),

        "createdAt": task.created_at,
        "completedAt": task.completed_at,
    }


# GET /tasks/
@router.get("/")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .join(Lead)
        .filter(Lead.owner_id == current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "count": len(tasks),
        "tasks": [
            task_response(task)
            for task in tasks
        ],
    }


# GET /tasks/{task_id}
@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .join(Lead)
        .filter(
            Task._id == task_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return {
        "success": True,
        "task": task_response(task),
    }


# POST /tasks/
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check lead belongs to current user
    lead = (
        db.query(Lead)
        .filter(
            Lead._id == task_data.related_lead_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    # Check contact if provided
    if task_data.related_contact_id is not None:
        contact = (
            db.query(Contact)
            .filter(
                Contact._id == task_data.related_contact_id,
                Contact.owner_id == current_user.id,
            )
            .first()
        )

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

    completed_at = None

    if task_data.status == TaskStatus.COMPLETED:
        completed_at = datetime.utcnow()

    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        status=task_data.status,
        priority=task_data.priority,
        related_lead_id=task_data.related_lead_id,
        related_contact_id=task_data.related_contact_id,
        completed_at=completed_at,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "success": True,
        "task": task_response(task),
    }


# PUT /tasks/{task_id}
@router.put("/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .join(Lead)
        .filter(
            Task._id == task_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    # If lead is changed
    if "related_lead_id" in update_data:
        lead = (
            db.query(Lead)
            .filter(
                Lead._id == update_data["related_lead_id"],
                Lead.owner_id == current_user.id,
            )
            .first()
        )

        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found",
            )

    # If contact is changed
    if "related_contact_id" in update_data:
        contact_id = update_data["related_contact_id"]

        if contact_id is not None:
            contact = (
                db.query(Contact)
                .filter(
                    Contact._id == contact_id,
                    Contact.owner_id == current_user.id,
                )
                .first()
            )

            if not contact:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contact not found",
                )

    # Update normal fields
    for field, value in update_data.items():
        setattr(task, field, value)

    # Handle completed_at
    if "status" in update_data:
        if update_data["status"] == TaskStatus.COMPLETED:
            if not task.completed_at:
                task.completed_at = datetime.utcnow()

        else:
            task.completed_at = None

    db.commit()
    db.refresh(task)

    return {
        "success": True,
        "task": task_response(task),
    }


# DELETE /tasks/{task_id}
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .join(Lead)
        .filter(
            Task._id == task_id,
            Lead.owner_id == current_user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {
        "success": True,
        "message": "Task deleted",
    }