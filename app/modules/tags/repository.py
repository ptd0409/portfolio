from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang
from app.modules.tags.schemas import TagSimple
from app.models.tag import Tag
from app.models.tag_translation import TagTranslation

async def list_tags(db: AsyncSession, lang: Lang) -> List[TagSimple]:
    stmt = (
        select(Tag, TagTranslation)
        .outerjoin(
            TagTranslation,
            (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang),
        )
        .order_by(Tag.id.asc())
    )

    rows = (await db.execute(stmt)).all()

    return [
        TagSimple(
            id=tag.id,
            slug=tag.slug,
            name=(tr.name if tr else None) or tag.slug,
        )
        for tag, tr in rows
    ]
