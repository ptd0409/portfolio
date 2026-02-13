from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.schemas.common import Lang, ApiResponse, Page
from app.modules.projects.schemas import ProjectListItem, ProjectDetail, ProjectCreate, ProjectRead
from app.modules.projects.repository import get_project_by_slug, list_projects_paginated_v2, create_project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ApiResponse[ProjectRead], status_code=201)
async def project_create(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        created = await create_project(db, payload)
        return ApiResponse(data=created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ApiResponse[Page[ProjectListItem]])
async def projects_list(
    lang: Lang = Query("vi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = Query("published"),
    db: AsyncSession = Depends(get_db)
):
    page_obj = await list_projects_paginated_v2(
        db=db,
        lang=lang,
        page=page,
        page_size=page_size,
        status=status
    )
    return ApiResponse(data=page_obj)

@router.get("/{slug}", response_model=ProjectDetail)
async def project_detail(
    slug: str,
    lang: Lang = "vi",
    status: str | None = "published",
    db: AsyncSession = Depends(get_db)
):
    project = await get_project_by_slug(db, slug=slug, lang=lang, status=status)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


