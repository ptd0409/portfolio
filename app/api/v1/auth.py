from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginInput(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginInput):
    if data.username != settings.ADMIN_USERNAME or data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "sub": data.username,
        "role": "admin"
    })

    return {
        "success": True,
        "message": "OK",
        "data": {
            "access_token": token,
            "token_type": "bearer"
        }
    }
