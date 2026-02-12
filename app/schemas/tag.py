from typing import List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema, IDSchema, TimestampMixin

class TagTranslationBase(BaseSchema):
    lang: str = Field(..., example="vi")
    name: str = Field(..., example="Backend")

class TagTranslationCreate(TagTranslationBase):
    pass

class TagTranslationUpdate(BaseSchema):
    name: Optional[str] = None

class TagTranslationRead(TagTranslationBase, IDSchema):
    pass

class TagBase(BaseSchema):
    slug: str = Field(..., example="backend")

class TagCreate(TagBase):
    translations: List[TagTranslationCreate]

class TagUpdate(BaseSchema):
    slug: Optional[str] = None

class TagRead(TagBase, IDSchema, TimestampMixin):
    translations: List[TagTranslationRead] = []

class TagSimple(BaseSchema, IDSchema):
    slug: str
    name: str = Field(..., description="Translated name or fallback slug")