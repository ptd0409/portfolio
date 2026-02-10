from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang

from app.schemas.project import ProjectListItem
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