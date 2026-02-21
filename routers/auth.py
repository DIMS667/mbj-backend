# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from typing import Annotated

from core.database import get_db
from core.security import verify_password, create_access_token
from core.deps import DBDep, CurrentUser
from models.user import User
from schemas.user import TokenOut, UserOut, UserCreate
from core.security import hash_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBDep,
):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Compte désactivé")

    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser):
    return current_user


# ── Route d'initialisation (à supprimer après le 1er déploiement) ──
@router.post("/init", response_model=UserOut, include_in_schema=False)
async def init_admin(payload: UserCreate, db: DBDep):
    """
    Crée le premier compte admin.
    Désactiver cette route après la création du compte.
    """
    result = await db.execute(select(User))
    if result.scalars().first():
        raise HTTPException(400, "Un compte existe déjà. Utilisez le backoffice.")

    user = User(
        email=payload.email,
        username=payload.username,
        password=hash_password(payload.password),
        is_admin=True,
    )
    db.add(user)
    await db.flush()
    return user