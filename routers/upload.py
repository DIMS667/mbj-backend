# routers/upload.py

import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

from core.config import settings
from core.deps import CurrentUser

router = APIRouter(prefix="/api/upload", tags=["Upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("")
async def upload_image(
    _: CurrentUser,
    file: UploadFile = File(...),
):
    # Vérifier le type MIME
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Type non supporté : {file.content_type}. Acceptés : JPEG, PNG, WEBP, GIF")

    content = await file.read()

    # Vérifier la taille
    if len(content) > MAX_BYTES:
        raise HTTPException(400, f"Fichier trop lourd (max {settings.MAX_FILE_SIZE_MB} Mo)")

    # Vérifier que c'est une vraie image
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(400, "Fichier image invalide ou corrompu")

    # Sauvegarder
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = upload_path / filename

    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    return JSONResponse({"url": f"/uploads/{filename}", "filename": filename})