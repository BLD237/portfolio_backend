from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import AdminUser
from app.services.content import dashboard_counts


router = APIRouter(prefix="/admin/dashboard", tags=["admin:dashboard"])


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return dashboard_counts(db)
