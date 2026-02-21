# routers/articles.py

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func
from slugify import slugify

from core.deps import DBDep, CurrentUser
from models.article import Article
from models.category import Category
from schemas.article import ArticleCreate, ArticleUpdate, ArticleOut, ArticleListOut

router = APIRouter(prefix="/api/articles", tags=["Articles"])

PER_PAGE_MAX = 50


# ── Admin (protégés) — déclarés AVANT /{slug} pour éviter les conflits ────────

@router.get("/admin/all", response_model=ArticleListOut)
async def list_articles_admin(
    db: DBDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=PER_PAGE_MAX),
    status: str | None = None,
    search: str | None = None,
):
    q = select(Article)
    if status:
        q = q.where(Article.status == status)
    if search:
        q = q.where(Article.title.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(Article.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return ArticleListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/admin/{article_id}", response_model=ArticleOut)
async def get_article_admin(article_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article introuvable")
    return article


@router.post("", response_model=ArticleOut, status_code=201)
async def create_article(payload: ArticleCreate, db: DBDep, current_user: CurrentUser):
    slug = payload.slug or slugify(payload.title)
    base_slug, counter = slug, 1
    while (await db.execute(select(Article).where(Article.slug == slug))).scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        counter += 1

    article = Article(
        **payload.model_dump(exclude={"slug"}),
        slug=slug,
        published_at=datetime.now(timezone.utc) if payload.status == "published" else None,
        author_id=current_user.id,
    )
    db.add(article)
    await db.flush()
    return article


@router.put("/{article_id}", response_model=ArticleOut)
async def update_article(article_id: int, payload: ArticleUpdate, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article introuvable")

    data = payload.model_dump(exclude_unset=True)
    if data.get("status") == "published" and article.status != "published":
        article.published_at = datetime.now(timezone.utc)
    if data.get("status") == "draft" and article.status == "published":
        article.published_at = None

    for key, value in data.items():
        setattr(article, key, value)
    await db.flush()
    return article


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article introuvable")
    await db.delete(article)


# ── Public — /{slug} en DERNIER pour ne pas capturer /admin/... ───────────────

@router.get("", response_model=ArticleListOut)
async def list_articles(
    db: DBDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=PER_PAGE_MAX),
    category: str | None = None,
    search: str | None = None,
):
    q = select(Article).where(Article.status == "published")
    if category:
        q = q.join(Category, Article.category_id == Category.id).where(Category.slug == category)
    if search:
        q = q.where(Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(Article.published_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return ArticleListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/{slug}", response_model=ArticleOut)
async def get_article(slug: str, db: DBDep):
    result = await db.execute(
        select(Article).where(Article.slug == slug, Article.status == "published")
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404, "Article introuvable")
    return article