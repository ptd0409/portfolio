from fastapi import Header, HTTPException
from app.core.config import settings

async def require_admin(x_api_key: str | None = Header(default=None)):
    if not getattr(settings, "ADMIN_API_KEY", None):
        return
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
