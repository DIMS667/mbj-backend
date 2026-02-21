# models/boutique.py

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class BoutiqueItem(Base):
    __tablename__ = "boutique_items"

    id:          Mapped[int]          = mapped_column(primary_key=True, index=True)
    name:        Mapped[str]          = mapped_column(String(255), nullable=False)
    slug:        Mapped[str]          = mapped_column(String(280), unique=True, index=True, nullable=False)
    description: Mapped[str | None]   = mapped_column(Text, nullable=True)
    content:     Mapped[str | None]   = mapped_column(Text, nullable=True)
    image_url:   Mapped[str | None]   = mapped_column(String(500), nullable=True)
    price:       Mapped[Decimal]      = mapped_column(Numeric(10, 2), nullable=False, default=0)
    in_stock:    Mapped[bool]         = mapped_column(Boolean, default=True)
    featured:    Mapped[bool]         = mapped_column(Boolean, default=False)
    status:      Mapped[str]          = mapped_column(
        SAEnum("draft", "published", name="boutique_status_enum"),
        default="draft",
        index=True,
    )
    category_id: Mapped[int | None]   = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    author_id:   Mapped[int | None]   = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at:  Mapped[datetime]     = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at:  Mapped[datetime]     = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", lazy="joined")
    author   = relationship("User", lazy="joined")