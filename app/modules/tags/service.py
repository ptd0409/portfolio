# modules/tags/service.py (hoặc repository.py)
from sqlalchemy import select, func
from app.models.tag import Tag
from app.models.tag_translation import TagTranslation

async def create_tag(db, payload):
    existed = await db.execute(select(Tag.id).where(Tag.slug == payload.slug))
    if existed.scalar_one_or_none() is not None:
        raise ValueError("slug already exists")

    tag = Tag(slug=payload.slug)
    db.add(tag)
    await db.flush()

    rows = []
    for tr in payload.translations:
        rows.append(TagTranslation(tag_id=tag.id, lang=tr.lang, name=tr.name))
    db.add_all(rows)

    await db.commit()
    return tag
