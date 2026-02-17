import os
import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from starlette import status

from app.api.deps import require_admin

router = APIRouter(prefix="/admin/media", tags=["admin-media"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = (BASE_DIR / "uploads").resolve()

ALLOWED = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_MB = 5

@router.post("/upload", dependencies=[Depends(require_admin)])
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        ext = ".jpg"

    key = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / key

    size = 0
    with path.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_MB * 1024 * 1024:
                out.close()
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large (> {MAX_MB}MB)",
                )
            out.write(chunk)

    return {
        "success": True,
        "message": "OK",
        "data": {
            "key": key,
            "url": f"/uploads/{key}",
            "mime": file.content_type,
            "size": size,
        },
    }
