# routers/categories.py

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from slugify import slugify

from core.deps import DBDep, CurrentUser
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["Catégories"])


# ── Public ───────────────────────────────────────────────────────────────────

@router.get("", response_model=list[CategoryOut])
async def list_categories(
    db: DBDep,
    type: str | None = Query(None, description="article | publication | boutique"),
):
    q = select(Category)
    if type:
        q = q.where(Category.content_type == type)
    result = await db.execute(q.order_by(Category.name))
    return result.scalars().all()


# ── Protégés (backoffice) ────────────────────────────────────────────────────

@router.post("", response_model=CategoryOut, status_code=201)
async def create_category(payload: CategoryCreate, db: DBDep, _: CurrentUser):
    slug = payload.slug or slugify(payload.name)
    existing = await db.execute(select(Category).where(Category.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Le slug '{slug}' est déjà utilisé")

    cat = Category(name=payload.name, slug=slug, content_type=payload.content_type)
    db.add(cat)
    await db.flush()
    return cat


@router.put("/{cat_id}", response_model=CategoryOut)
async def update_category(cat_id: int, payload: CategoryUpdate, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Catégorie introuvable")

    if payload.name is not None:
        cat.name = payload.name
    if payload.slug is not None:
        cat.slug = payload.slug
    await db.flush()
    return cat


@router.delete("/{cat_id}", status_code=204)
async def delete_category(cat_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Catégorie introuvable")
    await db.delete(cat)