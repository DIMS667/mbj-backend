# routers/boutique.py

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func
from slugify import slugify

from core.deps import DBDep, CurrentUser
from models.boutique import BoutiqueItem
from models.category import Category
from schemas.boutique import BoutiqueItemCreate, BoutiqueItemUpdate, BoutiqueItemOut, BoutiqueListOut

router = APIRouter(prefix="/api/boutique", tags=["Boutique"])

PER_PAGE_MAX = 50


# ── Admin (protégés) — déclarés AVANT /{slug} ─────────────────────────────────

@router.get("/admin/all", response_model=BoutiqueListOut)
async def list_items_admin(
    db: DBDep, _: CurrentUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=PER_PAGE_MAX),
    status: str | None = None,
    search: str | None = None,
):
    q = select(BoutiqueItem)
    if status: q = q.where(BoutiqueItem.status == status)
    if search: q = q.where(BoutiqueItem.name.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(BoutiqueItem.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return BoutiqueListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/admin/{item_id}", response_model=BoutiqueItemOut)
async def get_item_admin(item_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(BoutiqueItem).where(BoutiqueItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Produit introuvable")
    return item


@router.post("", response_model=BoutiqueItemOut, status_code=201)
async def create_item(payload: BoutiqueItemCreate, db: DBDep, current_user: CurrentUser):
    slug = payload.slug or slugify(payload.name)
    base_slug, counter = slug, 1
    while (await db.execute(select(BoutiqueItem).where(BoutiqueItem.slug == slug))).scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        counter += 1

    item = BoutiqueItem(
        **payload.model_dump(exclude={"slug"}),
        slug=slug,
        author_id=current_user.id,
    )
    db.add(item)
    await db.flush()
    return item


@router.put("/{item_id}", response_model=BoutiqueItemOut)
async def update_item(item_id: int, payload: BoutiqueItemUpdate, db: DBDep, _: CurrentUser):
    result = await db.execute(select(BoutiqueItem).where(BoutiqueItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Produit introuvable")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.flush()
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(BoutiqueItem).where(BoutiqueItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Produit introuvable")
    await db.delete(item)


# ── Public — en DERNIER ───────────────────────────────────────────────────────

@router.get("", response_model=BoutiqueListOut)
async def list_items(
    db: DBDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=PER_PAGE_MAX),
    category: str | None = None,
    search: str | None = None,
):
    q = select(BoutiqueItem).where(BoutiqueItem.status == "published")
    if category:
        q = q.join(Category, BoutiqueItem.category_id == Category.id).where(Category.slug == category)
    if search:
        q = q.where(BoutiqueItem.name.ilike(f"%{search}%") | BoutiqueItem.description.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        q.order_by(BoutiqueItem.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )).scalars().all()

    return BoutiqueListOut(
        items=items, total=total,
        total_pages=max(1, -(-total // per_page)),
        page=page, per_page=per_page,
    )


@router.get("/{slug}", response_model=BoutiqueItemOut)
async def get_item(slug: str, db: DBDep):
    result = await db.execute(
        select(BoutiqueItem).where(BoutiqueItem.slug == slug, BoutiqueItem.status == "published")
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Produit introuvable")
    return item