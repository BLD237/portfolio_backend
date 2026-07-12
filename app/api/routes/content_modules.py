from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import AdminUser
from app.schemas.content import ContentCreate, ContentUpdate
from app.services.content import (
    create_content,
    delete_content,
    get_content_by_slug,
    list_content,
    update_content,
)


def build_module_router(module: str) -> APIRouter:
    public_router = APIRouter(prefix=f"/{module}", tags=[module])
    admin_router = APIRouter(prefix=f"/admin/{module}", tags=[f"admin:{module}"])

    @public_router.get("")
    def public_list(db: Session = Depends(get_db)):
        return list_content(db, module, admin=False)

    @public_router.get("/{slug}")
    def public_detail(slug: str, db: Session = Depends(get_db)):
        return get_content_by_slug(db, module, slug)

    @admin_router.get("")
    def admin_list(
        db: Session = Depends(get_db),
        _: AdminUser = Depends(get_current_admin),
    ):
        return list_content(db, module, admin=True)

    @admin_router.post("", status_code=status.HTTP_201_CREATED)
    def admin_create(
        payload: ContentCreate,
        db: Session = Depends(get_db),
        _: AdminUser = Depends(get_current_admin),
    ):
        return create_content(db, module, payload)

    @admin_router.patch("/{item_id}")
    def admin_update(
        item_id: int,
        payload: ContentUpdate,
        db: Session = Depends(get_db),
        _: AdminUser = Depends(get_current_admin),
    ):
        return update_content(db, module, item_id, payload)

    @admin_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def admin_delete(
        item_id: int,
        db: Session = Depends(get_db),
        _: AdminUser = Depends(get_current_admin),
    ):
        delete_content(db, module, item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    router = APIRouter()
    router.include_router(public_router)
    router.include_router(admin_router)
    return router
