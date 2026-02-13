from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse, Page
from app.modules.projects.schemas import ProjectListItem, ProjectDetail, ProjectCreate, ProjectRead, ProjectUpdate
from app.modules.projects.repository import (
    get_project_by_slug,
    list_projects_paginated_v3,
    create_project,
    update_project_by_slug
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ApiResponse[ProjectRead], status_code=201)
async def project_create(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        created = await create_project(db, payload)
        return ApiResponse(data=created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ApiResponse[Page[ProjectListItem]] )
async def projects_list(
    lang: Lang = Query("vi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query("published"),
    q: Optional[str] = Query(None, min_length=1),
    tag_ids: Optional[str] = Query(None, description="Comma-separated tag ids, e.g. 1,2,3"),
    db: AsyncSession = Depends(get_db),
):
    ids: Optional[List[int]] = None
    if tag_ids:
        ids = [int(x) for x in tag_ids.split(",") if x.strip().isdigit()]

    page_obj = await list_projects_paginated_v3(
        db=db,
        lang=lang,
        page=page,
        page_size=page_size,
        status=status,
        q=q,
        tag_ids=ids,
    )
    return ApiResponse(data=page_obj)


@router.get("/{slug}", response_model=ApiResponse[ProjectDetail])
async def project_detail(
    slug: str,
    lang: Lang = Query("vi"),
    status: Optional[str] = Query("published"),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_by_slug(db, slug=slug, lang=lang, status=status)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=project)

@router.patch("/{slug}", response_model=ApiResponse[ProjectRead])
async def project_update(
    slug: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await update_project_by_slug(db, slug=slug, payload=payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Project not found")
        return ApiResponse(data=updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
