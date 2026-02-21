# models/category.py

from typing import Literal
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

# Les 3 types de rubriques
ContentType = Literal["article", "publication", "boutique"]


class Category(Base):
    __tablename__ = "categories"

    id:           Mapped[int] = mapped_column(primary_key=True, index=True)
    name:         Mapped[str] = mapped_column(String(100), nullable=False)
    slug:         Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    content_type: Mapped[str] = mapped_column(
        SAEnum("article", "publication", "boutique", name="content_type_enum"),
        nullable=False,
        index=True,
    )