from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


VALID_MODULES = {
    "projects",
    "blog",
    "articles",
    "gallery",
    "experience",
    "skills",
    "services",
    "testimonials",
    "credentials",
    "profile",
}
VALID_STATUSES = {"draft", "published", "archived"}


class ContentBase(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    slug: str = Field(min_length=2, max_length=220)
    summary: str = ""
    body: str = ""
    status: str = "published"
    sort_order: int = 0
    image_url: str = ""
    external_url: str = ""
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=220)
    slug: str | None = Field(default=None, min_length=2, max_length=220)
    summary: str | None = None
    body: str | None = None
    status: str | None = None
    sort_order: int | None = None
    image_url: str | None = None
    external_url: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ContentRead(ContentBase):
    id: int
    module: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=220)
    message: str = Field(min_length=5)


class ContactUpdate(BaseModel):
    status: str = Field(pattern="^(new|read|archived)$")


class ContactRead(ContactCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
