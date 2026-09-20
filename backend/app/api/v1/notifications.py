from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return [
        NotificationResponse(
            id=item.id,
            title=item.title,
            message=item.message,
            read=item.read
        )
        for item in notifs
    ]


@router.post("/mark-read")
def mark_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(Notification.user_id == current_user.id).update({"read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
