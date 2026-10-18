from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notes import Note
from app.models.contact import Contact
from app.schemas.note import NoteCreate, NoteUpdate

# Use your existing authentication dependency
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


def note_response(note: Note):
    return {
        "_id": note._id,
        "content": note.content,
        "contact": (
            {
                "_id": note.contact._id,
                "name": note.contact.name,
                "email": note.contact.email,
                "company": note.contact.company,
            }
            if note.contact
            else None
        ),
        "pinned": note.pinned,
        "createdAt": note.created_at,
    }


# GET /notes/
@router.get("/")
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .join(
            Contact,
            Note.contact_id == Contact._id,
            isouter=True,
        )
        .filter(
            (Contact.owner_id == current_user.id)
            | (Note.contact_id.is_(None))
        )
        .order_by(
            Note.pinned.desc(),
            Note.created_at.desc(),
        )
        .all()
    )

    return {
        "success": True,
        "count": len(notes),
        "notes": [
            note_response(note)
            for note in notes
        ],
    }


# GET /notes/{id}
@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        db.query(Note)
        .join(
            Contact,
            Note.contact_id == Contact._id,
            isouter=True,
        )
        .filter(
            Note._id == note_id,
            (
                (Contact.owner_id == current_user.id)
                | (Note.contact_id.is_(None))
            ),
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return {
        "success": True,
        "note": note_response(note),
    }


# POST /notes/
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If contact_id was provided, make sure it belongs
    # to the authenticated user.
    contact = None

    if note_data.contact_id is not None:
        contact = (
            db.query(Contact)
            .filter(
                Contact._id == note_data.contact_id,
                Contact.owner_id == current_user.id,
            )
            .first()
        )

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

    note = Note(
        content=note_data.content,
        contact_id=note_data.contact_id,
        pinned=note_data.pinned,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "success": True,
        "note": note_response(note),
    }


# PUT /notes/{id}
@router.put("/{note_id}")
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        db.query(Note)
        .join(
            Contact,
            Note.contact_id == Contact._id,
            isouter=True,
        )
        .filter(
            Note._id == note_id,
            (
                (Contact.owner_id == current_user.id)
                | (Note.contact_id.is_(None))
            ),
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    update_data = note_data.model_dump(
        exclude_unset=True
    )

    # If contact is being changed
    if "contact_id" in update_data:
        contact_id = update_data["contact_id"]

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

    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return {
        "success": True,
        "note": note_response(note),
    }


# DELETE /notes/{id}
@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        db.query(Note)
        .join(
            Contact,
            Note.contact_id == Contact._id,
            isouter=True,
        )
        .filter(
            Note._id == note_id,
            (
                (Contact.owner_id == current_user.id)
                | (Note.contact_id.is_(None))
            ),
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    db.delete(note)
    db.commit()

    return {
        "success": True,
        "message": "Note deleted",
    }