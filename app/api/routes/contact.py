from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import AdminUser
from app.models.content import ContactMessage
from app.schemas.content import ContactCreate, ContactRead, ContactUpdate
from app.services.email import send_contact_notification


router = APIRouter(tags=["contact"])


@router.post("/contact/messages", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_message(payload: ContactCreate, db: Session = Depends(get_db)):
    row = ContactMessage(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    
    # Send email notification
    try:
        send_contact_notification(
            sender_name=row.name,
            sender_email=row.email,
            subject=row.subject,
            message_text=row.message
        )
    except Exception as e:
        # Don't fail the response if email triggers an error
        pass
        
    return row


@router.get("/admin/contact/messages", response_model=list[ContactRead])
def list_messages(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()


@router.patch("/admin/contact/messages/{message_id}", response_model=ContactRead)
def update_message(
    message_id: int,
    payload: ContactUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    row = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not row:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    row.status = payload.status
    db.commit()
    db.refresh(row)
    return row


@router.delete("/admin/contact/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    row = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if row:
        db.delete(row)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
