from typing import List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema, IDSchema, TimestampMixin, Lang

class TagTranslationBase(BaseSchema):
    lang: Lang = Field(..., example="vi")
    name: str = Field(..., example="Backend")

class TagTranslationCreate(TagTranslationBase):
    pass

class TagTranslationUpdate(BaseSchema):
    lang: Lang
    name: Optional[str] = None

class TagTranslationRead(IDSchema, BaseSchema):
    lang: Lang
    name: str

class TagBase(BaseSchema):
    slug: str = Field(..., example="backend", min_length=1)

class TagTranslationIn(BaseSchema):
    lang: Lang
    name: str

class TagCreate(TagBase):
    translations: List[TagTranslationIn] = Field(default_factory=list)

class TagUpdate(BaseSchema):
    slug: Optional[str] = None
    translations: Optional[List[TagTranslationIn]] = None

class TagRead(IDSchema, TimestampMixin):
    slug: str
    translations: List[TagTranslationRead] = Field(default_factory=list)

class TagSimple(IDSchema):
    slug: str
    name: str = Field(..., description="Translated name or fallback slug")

class TagTranslationUpsert(BaseSchema):
    lang: Lang
    name: str = Field(..., min_length=1)

class TagUpdate(BaseSchema):
    slug: Optional[str] = Field(None, min_length=1)
    translations: Optional[List[TagTranslationUpsert]] = None

