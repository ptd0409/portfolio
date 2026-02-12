from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse
from app.schemas.tag import TagSimple
from app.models.tag import Tag
from app.models.tag_translation import TagTranslation

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("", response_model=ApiResponse[list[TagSimple]])
async def list_tags(
    lang: Lang = Query("vi"),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Tag, TagTranslation)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
        .order_by(Tag.id.asc())
    )
    rows = (await db.execute(stmt)).all()

    items: list[TagSimple] = []
    for tag, tr in rows:
        name = (tr.name if tr else None) or tag.slug
        items.append(TagSimple(id=tag.id, name=name))
    return ApiResponse(data=items)
