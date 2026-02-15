import math
from typing import List, Tuple, Dict, Optional
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang, PaginationMeta, Page

from app.modules.projects.schemas import ProjectListItem, ProjectDetail, ProjectCreate, ProjectRead, ProjectTranslationRead, ProjectUpdate, ProjectTranslationIn
from app.modules.tags.schemas import TagSimple
from app.models.project import Project
from app.models.project_translation import ProjectTranslation
from app.models.tag import Tag
from app.models.project_tag import ProjectTag
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

    count_stmt = (
        select(func.count(func.distinct(Project.id)))
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
    )
    if status is not None:
        count_stmt = count_stmt.where(Project.status == status)

    total_items = (await db.execute(count_stmt)).scalar_one()
    total_pages = 0 if total_items == 0 else math.ceil(total_items / page_size)

    ids_stmt = (
        select(Project.id)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
    )
    if status is not None:
        ids_stmt = ids_stmt.where(Project.status == status)

    ids_stmt = (
        ids_stmt
        .group_by(Project.id, Project.published_at)
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
        select(Project, ProjectTranslation, Tag, TagTranslation)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
        .outerjoin(Project.tags)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
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

    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    return Page(items=items, meta=meta)


async def create_project(db: AsyncSession, payload: ProjectCreate) -> ProjectRead:
    if not payload.slug:
        raise ValueError("slug is required")
    if not payload.translations:
        raise ValueError("translations must not be empty")
    
    langs: List[str] = [t.lang for t in payload.translations]
    if len(set(langs)) != len(langs):
        raise ValueError("translations.lang must be unique per project")
    
    existed = await db.execute(select(Project.id).where(Project.slug == payload.slug))
    if existed.scalar_one_or_none() is not None:
        raise ValueError("slug already exists")
    
    tag_ids: List[int] = list({int(x) for x in (payload.tag_ids or [])})
    if tag_ids:
        tag_count = await db.execute(select(func.count(Tag.id)).where(Tag.id.in_(tag_ids)))
        if tag_count.scalar_one() != len(tag_ids):
            raise ValueError("Some tag_ids do not exist")
    
    project = Project(
        slug=payload.slug,
        cover_image_url=payload.cover_image_url,
        repo_url=payload.repo_url,
        demo_url=payload.demo_url,
        status=payload.status or "draft",
        published_at=payload.published_at
    )
    db.add(project)
    await db.flush()

    tr_models: List[ProjectTranslation] = []
    for tr in payload.translations:
        tr_models.append(
            ProjectTranslation(
                project_id=project.id,
                lang=tr.lang,
                title=tr.title,
                summary=tr.summary,
                content_markdown=tr.content_markdown
            )
        )
    db.add_all(tr_models)
    await db.flush()

    for tid in tag_ids:
        db.add(ProjectTag(project_id=project.id, tag_id=tid))

    await db.commit()
    await db.refresh(project)

    tags: List[TagSimple] = []
    if tag_ids:
        tag_rows = (await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))).scalars().all()
        order = {tid: i for i, tid in enumerate(tag_ids)}
        tag_rows.sort(key=lambda t: order.get(t.id, 10**9))
        tags = [TagSimple(id=t.id, name=t.slug) for t in tag_rows]

    translations_read = [
        ProjectTranslationRead(
            id=t.id,
            lang=t.lang,
            title=t.title,
            summary=t.summary,
            content_markdown=t.content_markdown
        )
        for t in tr_models
    ]

    return ProjectRead(
        id=project.id,
        slug=project.slug,
        cover_image_url=project.cover_image_url,
        repo_url=project.repo_url,
        demo_url=project.demo_url,
        status=project.status,
        published_at=project.published_at,
        created_at=getattr(project, "created_at", None),
        updated_at=getattr(project, "updated_at", None),
        translations=translations_read,
        tags=tags
    )

async def list_projects_paginated_v3(
    db: AsyncSession,
    lang: Lang,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = "published",
    q: Optional[str] = None,
    tag_ids: Optional[List[int]] = None,
) -> Page[ProjectListItem]:
    page = max(int(page or 1), 1)
    page_size = max(1, min(int(page_size or 10), 100))
    offset = (page - 1) * page_size

    q_norm = (q or "").strip()
    has_q = len(q_norm) > 0
    like = f"%{q_norm}%"

    tag_ids = [int(x) for x in (tag_ids or []) if str(x).strip().isdigit()]
    tag_ids = list(dict.fromkeys(tag_ids))  # unique keep order (py3.7+)

    count_stmt = (
        select(func.count(func.distinct(Project.id)))
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
    )

    if status is not None:
        count_stmt = count_stmt.where(Project.status == status)

    if has_q:
        count_stmt = count_stmt.where(
            or_(
                Project.slug.ilike(like),
                ProjectTranslation.title.ilike(like),
                ProjectTranslation.summary.ilike(like),
            )
        )

    if tag_ids:
        count_stmt = (
            count_stmt
            .join(ProjectTag, ProjectTag.project_id == Project.id)
            .where(ProjectTag.tag_id.in_(tag_ids))
        )

    total_items = (await db.execute(count_stmt)).scalar_one()
    total_pages = 0 if total_items == 0 else math.ceil(total_items / page_size)

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

    ids_stmt = (
        select(Project.id)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
    )

    if status is not None:
        ids_stmt = ids_stmt.where(Project.status == status)

    if has_q:
        ids_stmt = ids_stmt.where(
            or_(
                Project.slug.ilike(like),
                ProjectTranslation.title.ilike(like),
                ProjectTranslation.summary.ilike(like),
            )
        )

    if tag_ids:
        ids_stmt = (
            ids_stmt
            .join(ProjectTag, ProjectTag.project_id == Project.id)
            .where(ProjectTag.tag_id.in_(tag_ids))
        )

    ids_stmt = (
        ids_stmt
        .group_by(Project.id, Project.published_at)
        .order_by(Project.published_at.desc().nullslast(), Project.id.desc())
        .limit(page_size)
        .offset(offset)
    )

    ids = [r[0] for r in (await db.execute(ids_stmt)).all()]

    if not ids:
        return Page(
            items=[],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )
    
    data_stmt = (
        select(Project, ProjectTranslation, Tag, TagTranslation)
        .join(ProjectTranslation, (ProjectTranslation.project_id == Project.id) & (ProjectTranslation.lang == lang))
        .outerjoin(ProjectTag, ProjectTag.project_id == Project.id)
        .outerjoin(Tag, Tag.id == ProjectTag.tag_id)
        .outerjoin(TagTranslation, (TagTranslation.tag_id == Tag.id) & (TagTranslation.lang == lang))
        .where(Project.id.in_(ids))
    )

    rows = (await db.execute(data_stmt)).unique().all()

    items_by_id: Dict[int, ProjectListItem] = {}
    seen_tags: Dict[int, set[int]] = {}

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
                tags=[],
            )
            seen_tags[pid] = set()

        if tag is not None and tag.id not in seen_tags[pid]:
            tag_name = (getattr(tag_tr, "name", None) if tag_tr is not None else None) or tag.slug
            items_by_id[pid].tags.append(TagSimple(id=tag.id, slug=tag.slug, name=tag_name))
            seen_tags[pid].add(tag.id)

    items = list(items_by_id.values())
    order_map = {pid: i for i, pid in enumerate(ids)}
    items.sort(key=lambda x: order_map.get(x.id, 10**9))

    return Page(
        items=items,
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )

def _dedupe_project_translations(translations) -> Dict[str, "ProjectTranslationIn"]:
    seen: Dict[str, "ProjectTranslationIn"] = {}
    for tr in translations:
        if tr.lang in seen:
            raise ValueError(f"duplicate translation lang: {tr.lang}")
        seen[tr.lang] = tr
    return seen


async def update_project_by_slug(
    db: AsyncSession,
    slug: str,
    payload: ProjectUpdate,
) -> Optional[ProjectRead]:
    project = (await db.execute(select(Project).where(Project.slug == slug))).scalar_one_or_none()
    if not project:
        return None

    if payload.slug is not None:
        new_slug = payload.slug.strip()
        if not new_slug:
            raise ValueError("slug must not be empty")

        if new_slug != project.slug:
            existed = await db.execute(select(Project.id).where(Project.slug == new_slug))
            if existed.scalar_one_or_none() is not None:
                raise ValueError("slug already exists")
            project.slug = new_slug

    if payload.cover_image_url is not None:
        project.cover_image_url = payload.cover_image_url

    if payload.repo_url is not None:
        project.repo_url = payload.repo_url

    if payload.demo_url is not None:
        project.demo_url = payload.demo_url

    if payload.status is not None:
        project.status = payload.status

    if payload.published_at is not None:
        project.published_at = payload.published_at

    if payload.translations is not None:
        tr_map = _dedupe_project_translations(payload.translations)

        current_rows = (
            await db.execute(select(ProjectTranslation).where(ProjectTranslation.project_id == project.id))
        ).scalars().all()

        current_by_lang: Dict[str, ProjectTranslation] = {t.lang: t for t in current_rows}

        for lang, tr in tr_map.items():
            if lang in current_by_lang:
                current_by_lang[lang].title = tr.title
                current_by_lang[lang].summary = tr.summary
                current_by_lang[lang].content_markdown = tr.content_markdown
            else:
                db.add(
                    ProjectTranslation(
                        project_id=project.id,
                        lang=tr.lang,
                        title=tr.title,
                        summary=tr.summary,
                        content_markdown=tr.content_markdown,
                    )
                )

    if payload.tag_ids is not None:
        tag_ids: List[int] = list({int(x) for x in payload.tag_ids})
        if tag_ids:
            tag_count = await db.execute(select(func.count(Tag.id)).where(Tag.id.in_(tag_ids)))
            if tag_count.scalar_one() != len(tag_ids):
                raise ValueError("Some tag_ids do not exist")

        await db.execute(delete(ProjectTag).where(ProjectTag.project_id == project.id))

        for tid in tag_ids:
            db.add(ProjectTag(project_id=project.id, tag_id=tid))

    await db.commit()
    await db.refresh(project)

    tr_rows = (
        await db.execute(select(ProjectTranslation).where(ProjectTranslation.project_id == project.id))
    ).scalars().all()

    translations_read = [
        ProjectTranslationRead(
            id=t.id,
            lang=t.lang,
            title=t.title,
            summary=t.summary,
            content_markdown=t.content_markdown,
        )
        for t in tr_rows
    ]

    tag_ids_rows = (
        await db.execute(select(ProjectTag.tag_id).where(ProjectTag.project_id == project.id))
    ).scalars().all()

    tags: List[TagSimple] = []
    if tag_ids_rows:
        tag_rows = (await db.execute(select(Tag).where(Tag.id.in_(tag_ids_rows)))).scalars().all()
        order = {tid: i for i, tid in enumerate(tag_ids_rows)}
        tag_rows.sort(key=lambda t: order.get(t.id, 10**9))
        tags = [TagSimple(id=t.id, slug=t.slug, name=t.slug) for t in tag_rows]

    return ProjectRead(
        id=project.id,
        slug=project.slug,
        cover_image_url=project.cover_image_url,
        repo_url=project.repo_url,
        demo_url=project.demo_url,
        status=project.status,
        published_at=project.published_at,
        created_at=getattr(project, "created_at", None),
        updated_at=getattr(project, "updated_at", None),
        translations=translations_read,
        tags=tags,
    )

async def delete_project_by_slug(db: AsyncSession, slug: str) -> bool:
    project = await db.execute(
        select(Project).where(Project.slug == slug)
    )
    project_obj = project.scalar_one_or_none()

    if not project_obj:
        return False

    await db.execute(
        delete(ProjectTag).where(ProjectTag.project_id == project_obj.id)
    )

    await db.execute(
        delete(ProjectTranslation).where(ProjectTranslation.project_id == project_obj.id)
    )

    await db.delete(project_obj)

    await db.commit()
    return True