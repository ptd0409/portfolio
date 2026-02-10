from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang

from app.schemas.project import ProjectListItem
from app.models.project import Project
from app.models.project_translation import ProjectTranslation
from app.models.tag_translation import TagTranslation

def list_projects(db: AsyncSession, lang: Lang, status: str | None = "published") -> List[ProjectListItem]:
    stmt = (
        select(Project).join(ProjectTranslation).where(ProjectTranslation.lang == lang).outerjoin(Project.tags).outerjoin(TagTranslation).where(TagTranslation.lang == lang)
    )