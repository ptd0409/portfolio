from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse, Page
from app.modules.tags.schemas import TagSimple, TagCreate, TagRead, TagUpdate
from app.modules.tags.repository import (
    list_tags_paginated,
    create_tag,
    get_tag,
    update_tag,
    delete_tag,
)

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=ApiResponse[Page[TagSimple]])
async def tags_list(
    lang: Lang = Query("vi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    data = await list_tags_paginated(db, lang=lang, page=page, page_size=page_size, q=q)
    return ApiResponse(data=data)


@router.post("", response_model=ApiResponse[TagRead], status_code=201)
async def tags_create(
    payload: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        tag = await create_tag(db, payload)
        return ApiResponse(data=tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tag_id}", response_model=ApiResponse[TagRead])
async def tags_get(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    tag = await get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return ApiResponse(data=tag)


@router.patch("/{tag_id}", response_model=ApiResponse[TagRead])
async def tags_update(
    tag_id: int,
    payload: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        tag = await update_tag(db, tag_id, payload)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return ApiResponse(data=tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", response_model=ApiResponse[bool])
async def tags_delete(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    ok = await delete_tag(db, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")
    return ApiResponse(data=True)
