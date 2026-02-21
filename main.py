# # main.py

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pathlib import Path
# from contextlib import asynccontextmanager

# from core.config import settings
# from core.database import engine, Base

# # Import de tous les modèles pour qu'Alembic les détecte
# import models.user        # noqa
# import models.category    # noqa
# import models.article     # noqa
# import models.publication # noqa
# import models.boutique    # noqa

# from routers import auth, categories, articles, publications, boutique, upload


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield
#     # Fermeture propre du pool sans greenlet
#     engine.sync_engine.dispose()


# # Créer le dossier uploads AVANT l'instanciation de FastAPI
# # (StaticFiles vérifie l'existence du dossier au démarrage)
# Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# app = FastAPI(
#     title=settings.APP_NAME,
#     version="1.0.0",
#     docs_url="/docs" if settings.APP_ENV != "production" else None,
#     redoc_url="/redoc" if settings.APP_ENV != "production" else None,
#     lifespan=lifespan,
# )

# # ── CORS ──────────────────────────────────────────────────────────────────────
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.allowed_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── Fichiers statiques (images uploadées) ─────────────────────────────────────
# app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# # ── Routers ───────────────────────────────────────────────────────────────────
# app.include_router(auth.router)
# app.include_router(categories.router)
# app.include_router(articles.router)
# app.include_router(publications.router)
# app.include_router(boutique.router)
# app.include_router(upload.router)


# @app.get("/", tags=["Health"])
# async def root():
#     return {"status": "ok", "app": settings.APP_NAME}


# @app.get("/health", tags=["Health"])
# async def health():
#     return {"status": "ok"}











# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine

# Import de tous les modèles pour qu'Alembic les détecte
import models.user        # noqa
import models.category    # noqa
import models.article     # noqa
import models.publication # noqa
import models.boutique    # noqa

from routers import auth, categories, articles, publications, boutique, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Fermeture propre du pool async — sans greenlet
    await engine.dispose()


# Créer le dossier uploads AVANT l'instanciation de FastAPI
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Fichiers statiques ─────────────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(articles.router)
app.include_router(publications.router)
app.include_router(boutique.router)
app.include_router(upload.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}