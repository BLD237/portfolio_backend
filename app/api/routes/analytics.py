from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import AdminUser
from app.services.analytics import log_visitor, get_analytics_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TrackPayload(BaseModel):
    path: str
    referrer: Optional[str] = "Direct"
    user_agent: Optional[str] = ""


@router.post("/track")
def track_visit(
    payload: TrackPayload,
    request: Request,
    db: Session = Depends(get_db)
):
    # Retrieve client IP, taking proxy headers like X-Forwarded-For into account
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Get the first IP in the list
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "127.0.0.1"

    # If user-agent is not passed, read from headers
    ua = payload.user_agent or request.headers.get("user-agent", "")

    log_visitor(
        db=db,
        ip_address=ip,
        path=payload.path,
        referrer=payload.referrer,
        user_agent=ua
    )
    return {"status": "tracked"}


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin)
):
    return get_analytics_stats(db)
