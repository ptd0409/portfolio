import math
from typing import List, Optional, Dict, Tuple
from sqlalchemy import select, delete, text, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.schemas.common import Lang, Page, PaginationMeta
from app.modules.tags.schemas import TagSimple
from app.models.tag import Tag
from app.models.tag_translation import TagTranslation
from app.modules.tags.schemas import TagSimple, TagCreate, TagRead, TagTranslationIn, TagUpdate, TagTranslationRead

def _dedupe_translations(translations: List[TagTranslationIn]) -> Dict[Lang, str]:
    """
    Dedupe theo lang. Nếu payload gửi trùng lang => raise ValueError.
    """
    seen: Dict[Lang, str] = {}
    for tr in translations:
        if tr.lang in seen:
            raise ValueError(f"duplicate translation lang: {tr.lang}")
        seen[tr.lang] = tr.name
    return seen

async def _to_tag_read(db: AsyncSession, tag: Tag) -> TagRead:
    """
    Map ORM Tag -> TagRead (kèm translations).
    Yêu cầu tag đã load translations hoặc query lại.
    """
    if not hasattr(tag, "tag_translations") or tag.tag_translations is None:
        tag = await db.get(Tag, tag.id, options=[selectinload(Tag.tag_translations)])

    translations = [
        TagTranslationRead(id=t.id, lang=t.lang, name=t.name) for t in (tag.tag_translations or [])
    ]

    return TagRead(
        id=tag.id,
        slug=tag.slug,
        created_at=getattr(tag, "created_at", None),
        updated_at=getattr(tag, "updated_at", None),
        translations=translations,
    )

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

async def get_tag(db: AsyncSession, tag_id: int) -> Optional[TagRead]:
    tag = await db.get(Tag, tag_id, options=[selectinload(Tag.tag_translations)])
    if not tag:
        return None
    return await _to_tag_read(db, tag)

async def create_tag(db: AsyncSession, payload: TagCreate) -> TagRead:
    existed = await db.execute(select(Tag.id).where(Tag.slug == payload.slug))
    if existed.scalar_one_or_none() is not None:
        raise ValueError("slug already exist")
    
    tag = Tag(slug=payload.slug)
    db.add(tag)
    await db.flush()

    for tr in (payload.translations or []):
        db.add(
            TagTranslation(tag_id=tag.id, lang=tr.lang, name=tr.name)
        )

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("slug already exists")

    tag = await db.get(Tag, tag.id, options=[selectinload(Tag.tag_translations)])

    return await _to_tag_read(db, tag)

async def update_tag(db: AsyncSession, tag_id: int, payload: TagUpdate) -> Optional[TagRead]:
    tag = await db.get(Tag, tag_id, options=[selectinload(Tag.tag_translations)])
    if not tag:
        return None

    if payload.slug is not None:
        new_slug = payload.slug.strip()
        if not new_slug:
            raise ValueError("slug must not be empty")

        if new_slug != tag.slug:
            existed = await db.execute(
                select(Tag.id).where(Tag.slug == new_slug, Tag.id != tag_id)
            )
            if existed.scalar_one_or_none() is not None:
                raise ValueError("slug already exists")
            tag.slug = new_slug

    if payload.translations is not None:
        tr_map = _dedupe_translations(payload.translations)

        current_by_lang: Dict[Lang, TagTranslation] = {
            t.lang: t for t in (tag.tag_translations or [])
        }

        for lang, name in tr_map.items():
            if lang in current_by_lang:
                current_by_lang[lang].name = name
            else:
                db.add(TagTranslation(tag_id=tag.id, lang=lang, name=name))

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("slug already exists")

    await db.refresh(tag)

    tag = await db.get(Tag, tag.id, options=[selectinload(Tag.tag_translations)])
    return await _to_tag_read(db, tag)


async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
    tag = await db.get(Tag, tag_id)
    if not tag:
        return False

    await db.execute(text("DELETE FROM project_tags WHERE tag_id = :tid"), {"tid": tag_id})
    await db.execute(delete(TagTranslation).where(TagTranslation.tag_id == tag_id))
    await db.delete(tag)

    await db.commit()
    return True

async def list_tags_paginated(
    db: AsyncSession,
    lang: Lang,
    page: int = 1,
    page_size: int = 10,
    q: Optional[str] = None,
) -> Page[TagSimple]:
    page = max(1, int(page))
    page_size = max(1, min(100, int(page_size)))
    offset = (page - 1) * page_size

    q_norm = (q or "").strip()
    has_q = len(q_norm) > 0
    like = f"%{q_norm}%"

    count_stmt = (
        select(func.count(func.distinct(Tag.id)))
        .outerjoin(
            TagTranslation,
            (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang),
        )
    )

    if has_q:
        count_stmt = count_stmt.where(
            or_(
                Tag.slug.ilike(like),
                TagTranslation.name.ilike(like),
            )
        )

    total_items = (await db.execute(count_stmt)).scalar_one()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

    if total_pages > 0 and page > total_pages:
        return Page(
            items=[],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    items_stmt = (
        select(Tag, TagTranslation)
        .outerjoin(
            TagTranslation,
            (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang),
        )
        .order_by(Tag.id.asc())
        .limit(page_size)
        .offset(offset)
    )

    if has_q:
        items_stmt = items_stmt.where(
            or_(
                Tag.slug.ilike(like),
                TagTranslation.name.ilike(like),
            )
        )

    rows: List[Tuple[Tag, Optional[TagTranslation]]] = (await db.execute(items_stmt)).all()

    items = [
        TagSimple(
            id=tag.id,
            slug=tag.slug,
            name=(tr.name if tr else None) or tag.slug,  # fallback
        )
        for tag, tr in rows
    ]

    return Page(
        items=items,
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )