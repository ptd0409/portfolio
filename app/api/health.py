from fastapi import APIRouter
from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=ApiResponse[dict])
async def health():
    return ApiResponse(data={"status": "ok"})
