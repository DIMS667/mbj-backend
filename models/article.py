# models/article.py

from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id:           Mapped[int]            = mapped_column(primary_key=True, index=True)
    title:        Mapped[str]            = mapped_column(String(255), nullable=False)
    slug:         Mapped[str]            = mapped_column(String(280), unique=True, index=True, nullable=False)
    excerpt:      Mapped[str | None]     = mapped_column(Text, nullable=True)
    content:      Mapped[str]            = mapped_column(Text, nullable=False, default="")
    image_url:    Mapped[str | None]     = mapped_column(String(500), nullable=True)
    status:       Mapped[str]            = mapped_column(
        SAEnum("draft", "published", name="article_status_enum"),
        default="draft",
        index=True,
    )
    category_id:  Mapped[int | None]     = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    author_id:    Mapped[int | None]     = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:   Mapped[datetime]        = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at:   Mapped[datetime]        = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relations
    category = relationship("Category", lazy="joined")
    author   = relationship("User", lazy="joined")