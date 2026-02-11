import math
from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang, PaginationMeta, Page

from app.schemas.project import ProjectListItem
from app.schemas.project import ProjectDetail
from app.schemas.tag import TagSimple
from app.models.project import Project
from app.models.project_translation import ProjectTranslation
from app.models.tag import Tag
from app.models.tag_translation import TagTranslation

async def list_projects(db: AsyncSession, lang: Lang, status: str | None = "published") -> List[ProjectListItem]:
    stmt = (
        select(Project, ProjectTranslation, Tag, TagTranslation)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
        .outerjoin(Project.tags)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
        .order_by(Project.published_at.desc())
    )

    if status is not None:
        stmt = stmt.where(Project.status == status)

    result = await db.execute(stmt)
    rows = result.unique().all()
    items_by_id: dict[int, ProjectListItem] = {}
    seen_tags: dict[int, set[int]] = {}

    for project, project_tr, tag, tag_tr in rows:
        pid = project.id

        if pid not in items_by_id:
            items_by_id[pid] = ProjectListItem(
                id=project.id,
                slug=project.slug,
                cover_image_url=getattr(project, "cover_image_url", None),
                repo_url=getattr(project, "repo_url", None),
                demo_url=getattr(project, "demo_url", None),
                status=getattr(project, "status", None),
                published_at=getattr(project, "published_at", None),
                title=project_tr.title,
                summary=project_tr.summary,
                tags=[],
            )
            seen_tags[pid] = set()
        
        if tag is not None and tag.id not in seen_tags[pid]:
            tag_name = None
            if tag_tr is not None:
                tag_name = getattr(tag_tr, "name", None)
            
            items_by_id[pid].tags.append(
                TagSimple(
                    id=tag.id,
                    name=tag_name or tag.slug,
                )
            )
            seen_tags[pid].add(tag.id)

    return list(items_by_id.values())

async def get_project_by_slug(db: AsyncSession, slug: str, lang: Lang, status: str | None = "published") -> ProjectDetail | None:
    stmt = (
        select(Project, ProjectTranslation, Tag, TagTranslation)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
        .outerjoin(Project.tags)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
        .where(Project.slug == slug)
    )

    if status is not None:
        stmt = stmt.where(Project.status == status)
    
    result = await db.execute(stmt)
    rows = result.unique().all()
    if not rows:
        return None
    project, project_tr, _, _ = rows[0]

    tags: List[TagSimple] = []
    seen = set()
    for _, _, tag, tag_tr in rows:
        if tag and tag.id not in seen:
            tags.append(TagSimple(id=tag.id, name=(tag_tr.name if tag_tr else None) or tag.slug))
            seen.add(tag.id)

    return ProjectDetail(
        id=project.id,
        slug=project.slug,
        cover_image_url=getattr(project, "cover_image_url", None),
        repo_url=getattr(project, "repo_url", None),
        demo_url=getattr(project, "demo_url", None),
        status=getattr(project, "status", None),
        published_at=getattr(project, "published_at", None),
        title=project_tr.title,
        summary=project_tr.summary,
        content_markdown=project_tr.content_markdown,
        tags=tags,
    )

async def list_projects_paginated(
        db: AsyncSession,
        lang: Lang,
        page: int = 1,
        page_size: int = 10,
        status: str | None = "published"
) -> Tuple[List[ProjectListItem], PaginationMeta]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size

    count_stmt = (
        select(func.count(func.distinct(Project.id)))
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang ))
    )
    if status is not None:
        count_stmt = count_stmt.where(Project.status == status)
    
    total_items = (await db.execute(count_stmt)).scalar_one()
    total_pages = max(1, math.ceil(total_items / page_size)) if total_items else 1

    stmt = (
        select(Project, ProjectTranslation, Tag, TagTranslation)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
        .outerjoin(Project.tags)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
        .order_by(Project.published_at.desc().nullslast(), Project.id.desc())
        .limit(page_size)
        .offset(offset)
    )
    if status is not None:
        stmt = stmt.where(Project.status == status)

    rows = (await db.execute(stmt)).unique().all()

    items_by_id: dict[int, ProjectListItem] = {}
    seen_tags: dict[int, set[int]] = {}

    for project, project_tr, tag, tag_tr in rows:
        pid = project.id
        if pid not in items_by_id:
            items_by_id[pid] = ProjectListItem(
                id=project.id,
                slug=project.slug,
                cover_image_url=getattr(project, "cover_image_url", None),
                repo_url=getattr(project, "repo_url", None),
                demo_url=getattr(project, "demo_url", None),
                status=getattr(project, "status", None),
                published_at=getattr(project, "published_at", None),
                title=project_tr.title,
                summary=project_tr.summary,
                tags=[],
            )
            seen_tags[pid] = set()

        if tag is not None and tag.id not in seen_tags[pid]:
            tag_name = (getattr(tag_tr, "name", None) if tag_tr is not None else None) or tag.slug
            items_by_id[pid].tags.append(TagSimple(id=tag.id, name=tag_name))
            seen_tags[pid].add(tag.id)

    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    return list(items_by_id.values()), meta

async def list_projects_paginated_v2(
        db: AsyncSession,
        lang: Lang,
        page: int = 1,
        page_size: int = 10,
        status: str | None = "published"
) -> Page[ProjectListItem]:
    page = max(int(page or 1), 1)
    page_size = int(page_size or 10)
    page_size = max(1, min(page_size, 100))
    offset = (page -1)*page_size

    PT = aliased(ProjectTranslation)
    TT = aliased(TagTranslation)

    count_stmt = (
        select(func.count(func.distinct(Project.id)))
        .join(PT, (PT.project_id == Project.id) & (PT.lang == lang))
    )
    if status is not None:
        count_stmt = count_stmt.where(Project.status == status)

    total_items = (await db.execute(count_stmt)).scalar_one()
    total_pages = 0 if total_items == 0 else math.ceil(total_items / page_size)

    ids_stmt = (
        select(Project.id)
        .join(PT, (PT.project_id == Project.id) & (PT.lang == lang))
    )
    if status is not None:
        ids_stmt = ids_stmt.where(Project.status == status)

    ids_stmt = (
        ids_stmt.distinct()
        .order_by(Project.published_at.desc().nullslast(), Project.id.desc())
        .limit(page_size)
        .offset(offset)
    )

    ids = [r[0] for r in (await db.execute(ids_stmt)).all()]

    if not ids:
        return Page(
            items=[],
            meta={
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
        )
    
    data_stmt = (
        select(Project, PT, Tag, TT)
        .join(PT, (PT.project_id == Project.id) & (PT.lang == lang))
        .outerjoin(Project.tags)
        .outerjoin(TT, (TT.tag_id == Tag.id) & (TT.lang == lang))
        .where(Project.id.in_(ids))
    )

    rows = (await db.execute(data_stmt)).unique().all()

    items_by_id: dict[int, ProjectListItem] = {}
    seen_tags: dict[int, set[int]] = {}

    for project, project_tr, tag, tag_tr in rows:
        pid = project.id
        if pid not in items_by_id:
            items_by_id[pid] = ProjectListItem(
                id=project.id,
                slug=project.slug,
                cover_image_url=getattr(project, "cover_image_url", None),
                repo_url=getattr(project, "repo_url", None),
                demo_url=getattr(project, "demo_url", None),
                status=project.status,
                published_at=project.published_at,
                title=project_tr.title,
                summary=getattr(project_tr, "summary", None),
                tags=[]
            )
            seen_tags[pid] = set()

        if tag is not None:
            if tag.id not in seen_tags[pid]:
                items_by_id[pid].tags.append(
                    TagSimple(
                        id=tag.id,
                        name=((tag_tr.name if tag_tr else None) or tag.slug)
                    )
                )
                seen_tags[pid].add(tag.id)
    items = list(items_by_id.values())
    order = {id_: i for i, id_ in enumerate(ids)}
    items.sort(key=lambda x: order.get(x.id, 10**9))

    return Page(
    items=[],
    meta=PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    ),
)
