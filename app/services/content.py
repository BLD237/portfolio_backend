import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.content import ContactMessage, ContentItem
from app.schemas.content import ContentCreate, ContentUpdate, VALID_MODULES, VALID_STATUSES


def ensure_module(module: str) -> str:
    if module not in VALID_MODULES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown portfolio module")
    return module


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def serialize_content(item: ContentItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "module": item.module,
        "title": item.title,
        "slug": item.slug,
        "summary": item.summary,
        "body": item.body,
        "status": item.status,
        "sort_order": item.sort_order,
        "image_url": item.image_url,
        "external_url": item.external_url,
        "tags": _loads(item.tags, []),
        "metadata": _loads(item.metadata_json, {}),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def list_content(db: Session, module: str, admin: bool = False) -> list[dict[str, Any]]:
    ensure_module(module)
    query = db.query(ContentItem).filter(ContentItem.module == module)
    if not admin:
        query = query.filter(ContentItem.status == "published")
    rows = query.order_by(ContentItem.sort_order.asc(), ContentItem.created_at.desc()).all()
    return [serialize_content(row) for row in rows]


def get_content_by_slug(db: Session, module: str, slug: str) -> dict[str, Any]:
    ensure_module(module)
    row = (
        db.query(ContentItem)
        .filter(ContentItem.module == module, ContentItem.slug == slug, ContentItem.status == "published")
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return serialize_content(row)


def get_content_by_id(db: Session, module: str, item_id: int) -> ContentItem:
    ensure_module(module)
    row = db.query(ContentItem).filter(ContentItem.module == module, ContentItem.id == item_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return row


def create_content(db: Session, module: str, payload: ContentCreate) -> dict[str, Any]:
    ensure_module(module)
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")
    row = ContentItem(
        module=module,
        title=payload.title,
        slug=payload.slug,
        summary=payload.summary,
        body=payload.body,
        status=payload.status,
        sort_order=payload.sort_order,
        image_url=payload.image_url,
        external_url=payload.external_url,
        tags=json.dumps(payload.tags),
        metadata_json=json.dumps(payload.metadata),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_content(row)


def update_content(db: Session, module: str, item_id: int, payload: ContentUpdate) -> dict[str, Any]:
    row = get_content_by_id(db, module, item_id)
    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")

    for key, value in updates.items():
        if key == "metadata":
            setattr(row, "metadata_json", json.dumps(value or {}))
        elif key == "tags":
            setattr(row, "tags", json.dumps(value or []))
        else:
            setattr(row, key, value)

    db.commit()
    db.refresh(row)
    return serialize_content(row)


def delete_content(db: Session, module: str, item_id: int) -> None:
    row = get_content_by_id(db, module, item_id)
    db.delete(row)
    db.commit()


def dashboard_counts(db: Session) -> dict[str, Any]:
    modules = {module: db.query(ContentItem).filter(ContentItem.module == module).count() for module in sorted(VALID_MODULES)}
    messages = {
        "total": db.query(ContactMessage).count(),
        "new": db.query(ContactMessage).filter(ContactMessage.status == "new").count(),
    }
    return {"modules": modules, "messages": messages}
