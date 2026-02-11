from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse, Page
from app.schemas.project import ProjectListItem, ProjectDetail
from app.crud.project import list_projects, get_project_by_slug, list_projects_paginated

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectListItem])
async def projects_list(lang: Lang = "vi", db: AsyncSession = Depends(get_db)):
    return await list_projects(db, lang)

@router.get("/{slug}", response_model=ProjectDetail)
async def project_detail(slug: str, lang: Lang = "vi", db: AsyncSession = Depends(get_db)):
    project = await get_project_by_slug(db, slug=slug, lang=lang)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("", response_model=ApiResponse[Page[ProjectListItem]])
async def projects_list(
    lang: Lang = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query("published"),
    db: AsyncSession = Depends(get_db)
):
    items, meta = await list_projects_paginated(db=db, lang=lang, page=page, page_size=page_size, status=status)
    return ApiResponse(data=Page(items=items, meta=meta))
    