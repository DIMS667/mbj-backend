# schemas/article.py

from datetime import datetime
from pydantic import BaseModel
from schemas.category import CategoryOut
from schemas.user import UserOut


class ArticleBase(BaseModel):
    title: str
    excerpt: str | None = None
    content: str = ""
    image_url: str | None = None
    category_id: int | None = None
    status: str = "draft"


class ArticleCreate(ArticleBase):
    slug: str | None = None   # Auto-généré si absent


class ArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    excerpt: str | None = None
    content: str | None = None
    image_url: str | None = None
    category_id: int | None = None
    status: str | None = None


class ArticleOut(ArticleBase):
    id: int
    slug: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    category: CategoryOut | None = None
    author: UserOut | None = None

    model_config = {"from_attributes": True}


class ArticleListOut(BaseModel):
    items: list[ArticleOut]
    total: int
    total_pages: int
    page: int
    per_page: int