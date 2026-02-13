from datetime import datetime
from typing import List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema, TimestampMixin, Lang, IDSchema
from app.modules.tags.schemas import TagSimple

class ProjectTranslationBase(BaseSchema):
    lang: Lang = Field(..., example="vi")
    title: str
    summary: Optional[str] = Field(None, example="This backend is built with Fastapi")
    content_markdown: Optional[str] = Field(None, example="This is content in markdown")

class ProjectTranslationCreate(ProjectTranslationBase):
    pass

class ProjectTranslationUpdate(BaseSchema):
    lang: Lang = Field(..., example="vi")
    summary: Optional[str] = None
    content_markdown: Optional[str] = None

class ProjectTranslationRead(ProjectTranslationBase,IDSchema):
    pass

class ProjectBase(BaseSchema):
    slug: Optional[str] = None
    cover_image_url: Optional[str] = Field(None)
    repo_url: Optional[str] = Field(None)
    demo_url: Optional[str] = Field(None)
    status: Optional[str] = None
    published_at: Optional[datetime] = Field(None)

class ProjectCreate(ProjectBase):
    translations: List[ProjectTranslationCreate] = Field(default_factory=list)
    tag_ids: List[int] = Field(default_factory=list)

class ProjectUpdate(BaseSchema):
    slug: Optional[str] = None
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[datetime] = None
    translations: Optional[List[ProjectTranslationUpdate]] = None
    tag_ids: Optional[List[int]] = None

class ProjectListItem(BaseSchema):
    id: int
    slug: Optional[str] = None
    cover_image_url: Optional[str] = Field(None)
    repo_url: Optional[str] = Field(None)
    demo_url: Optional[str] = Field(None)
    status: Optional[str] = None
    published_at: Optional[datetime] = Field(None)
    title: str = Field(...)
    summary: Optional[str] = Field(None)
    tags: List[TagSimple] = Field(default_factory=list)

class ProjectDetail(ProjectListItem):
    content_markdown: Optional[str] = None

class ProjectRead(ProjectBase, IDSchema, TimestampMixin):
    translations: List[ProjectTranslationRead] = Field(default_factory=list)
    tags: List[TagSimple] = Field(default_factory=list)

class ProjectTranslationIn(BaseSchema):
    lang: Lang
    title: str
    summary: str
    content_markdown: str

class ProjectUpdate(BaseSchema):
    slug: Optional[str] = Field(default=None, min_length=1)
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[str] = None
    translations: Optional[List[ProjectTranslationIn]] = None
    tag_ids: Optional[List[int]] = None