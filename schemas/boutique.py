# schemas/boutique.py

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from schemas.category import CategoryOut
from schemas.user import UserOut


class BoutiqueItemBase(BaseModel):
    name: str
    description: str | None = None
    content: str | None = None
    image_url: str | None = None
    price: Decimal = Decimal("0")
    in_stock: bool = True
    featured: bool = False
    category_id: int | None = None
    status: str = "draft"


class BoutiqueItemCreate(BoutiqueItemBase):
    slug: str | None = None


class BoutiqueItemUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    content: str | None = None
    image_url: str | None = None
    price: Decimal | None = None
    in_stock: bool | None = None
    featured: bool | None = None
    category_id: int | None = None
    status: str | None = None


class BoutiqueItemOut(BoutiqueItemBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    category: CategoryOut | None = None
    author: UserOut | None = None

    model_config = {"from_attributes": True}


class BoutiqueListOut(BaseModel):
    items: list[BoutiqueItemOut]
    total: int
    total_pages: int
    page: int
    per_page: int