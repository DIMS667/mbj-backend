# schemas/category.py

from typing import Literal
from pydantic import BaseModel

ContentType = Literal["article", "publication", "boutique"]


class CategoryBase(BaseModel):
    name: str
    content_type: ContentType


class CategoryCreate(CategoryBase):
    slug: str | None = None   # Auto-généré depuis le name si absent


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class CategoryOut(CategoryBase):
    id: int
    slug: str

    model_config = {"from_attributes": True}