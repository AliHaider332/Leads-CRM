from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
)

# Change this import to match your authentication setup
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


def contact_response(contact: Contact):
    return {
        "_id": contact._id,
        "name": contact.name,
        "title": contact.title,
        "company": contact.company,
        "email": contact.email,
        "phone": contact.phone,
        "tags": contact.tags or [],
        "favorite": contact.favorite,
        "createdAt": contact.created_at,
        "updatedAt": contact.updated_at,
    }


# GET /contacts
@router.get("/")
def list_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts = (
        db.query(Contact)
        .filter(Contact.owner_id == current_user.id)
        .order_by(Contact.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "count": len(contacts),
        "contacts": [
            contact_response(contact)
            for contact in contacts
        ],
    }


# GET /contacts/{id}
@router.get("/{contact_id}")
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    return {
        "success": True,
        "contact": contact_response(contact),
    }


# POST /contacts
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = Contact(
        owner_id=current_user.id,
        name=contact_data.name,
        title=contact_data.title,
        company=contact_data.company,
        email=contact_data.email,
        phone=contact_data.phone,
        tags=contact_data.tags,
        favorite=contact_data.favorite,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {
        "success": True,
        "contact": contact_response(contact),
    }


# PUT /contacts/{id}
@router.put("/{contact_id}")
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    update_data = contact_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return {
        "success": True,
        "contact": contact_response(contact),
    }


# DELETE /contacts/{id}
@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    db.delete(contact)
    db.commit()

    return {
        "success": True,
        "message": "Contact deleted",
    }