# schemas/publication.py

from datetime import datetime
from pydantic import BaseModel
from schemas.category import CategoryOut
from schemas.user import UserOut


class PublicationBase(BaseModel):
    title: str
    excerpt: str | None = None
    content: str = ""
    image_url: str | None = None
    category_id: int | None = None
    status: str = "draft"


class PublicationCreate(PublicationBase):
    slug: str | None = None


class PublicationUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    excerpt: str | None = None
    content: str | None = None
    image_url: str | None = None
    category_id: int | None = None
    status: str | None = None


class PublicationOut(PublicationBase):
    id: int
    slug: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    category: CategoryOut | None = None
    author: UserOut | None = None

    model_config = {"from_attributes": True}


class PublicationListOut(BaseModel):
    items: list[PublicationOut]
    total: int
    total_pages: int
    page: int
    per_page: int