import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/admin/media", tags=["media"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/gif"}

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = Path(file.filename or "").suffix.lower() or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / name

    content = await file.read()
    path.write_bytes(content)

    return {"success": True, "message": "OK", "data": {"url": f"/uploads/{name}"}}
