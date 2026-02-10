from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import Lang

from app.schemas.project import ProjectListItem

def list_projects(db: AsyncSession, lang: Lang, status: str | None = "published") -> List[ProjectListItem]:
    pass