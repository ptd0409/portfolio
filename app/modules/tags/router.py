from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse
from app.modules.tags.schemas import TagSimple
from app.modules.tags.repository import list_tags

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=ApiResponse[list[TagSimple]])
async def tags_list(lang: Lang = Query("vi"), db: AsyncSession = Depends(get_db)):
    return ApiResponse(data=await list_tags(db, lang))
