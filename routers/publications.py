# routers/publications.py

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func
from slugify import slugify

from core.deps import DBDep, CurrentUser
from models.publication import Publication
from models.category import Category
from schemas.publication import PublicationCreate, PublicationUpdate, PublicationOut, PublicationListOut

router = APIRouter(prefix="/api/publications", tags=["Publications"])

PER_PAGE_MAX = 50


# ── Admin (protégés) — déclarés AVANT /{slug} ─────────────────────────────────

@router.get("/admin/all", response_model=PublicationListOut)
async def list_publications_admin(
    db: DBDep, _: CurrentUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=PER_PAGE_MAX),
    status: str | None = None,
    search: str | None = None,
):
    q = select(Publication)
    if status: q = q.where(Publication.status == status)
    if search: q = q.where(Publication.title.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(Publication.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return PublicationListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/admin/{pub_id}", response_model=PublicationOut)
async def get_publication_admin(pub_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Publication).where(Publication.id == pub_id))
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(404, "Publication introuvable")
    return pub


@router.post("", response_model=PublicationOut, status_code=201)
async def create_publication(payload: PublicationCreate, db: DBDep, current_user: CurrentUser):
    slug = payload.slug or slugify(payload.title)
    base_slug, counter = slug, 1
    while (await db.execute(select(Publication).where(Publication.slug == slug))).scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        counter += 1

    pub = Publication(
        **payload.model_dump(exclude={"slug"}),
        slug=slug,
        published_at=datetime.now(timezone.utc) if payload.status == "published" else None,
        author_id=current_user.id,
    )
    db.add(pub)
    await db.flush()
    return pub


@router.put("/{pub_id}", response_model=PublicationOut)
async def update_publication(pub_id: int, payload: PublicationUpdate, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Publication).where(Publication.id == pub_id))
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(404, "Publication introuvable")

    data = payload.model_dump(exclude_unset=True)
    if data.get("status") == "published" and pub.status != "published":
        pub.published_at = datetime.now(timezone.utc)
    if data.get("status") == "draft" and pub.status == "published":
        pub.published_at = None

    for key, value in data.items():
        setattr(pub, key, value)
    await db.flush()
    return pub


@router.delete("/{pub_id}", status_code=204)
async def delete_publication(pub_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Publication).where(Publication.id == pub_id))
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(404, "Publication introuvable")
    await db.delete(pub)


# ── Public — en DERNIER ───────────────────────────────────────────────────────

@router.get("", response_model=PublicationListOut)
async def list_publications(
    db: DBDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=PER_PAGE_MAX),
    category: str | None = None,
    search: str | None = None,
):
    q = select(Publication).where(Publication.status == "published")
    if category:
        q = q.join(Category, Publication.category_id == Category.id).where(Category.slug == category)
    if search:
        q = q.where(Publication.title.ilike(f"%{search}%") | Publication.content.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(Publication.published_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return PublicationListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/{slug}", response_model=PublicationOut)
async def get_publication(slug: str, db: DBDep):
    result = await db.execute(
        select(Publication).where(Publication.slug == slug, Publication.status == "published")
    )
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(404, "Publication introuvable")
    return pub