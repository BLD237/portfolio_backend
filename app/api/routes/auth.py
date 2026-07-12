from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.admin import AdminUser
from app.schemas.auth import AdminUserRead, LoginRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    admin = db.query(AdminUser).filter(AdminUser.email == payload.email).first()
    if not admin or not admin.is_active or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(admin.email))


@router.get("/me", response_model=AdminUserRead)
def me(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    return admin
