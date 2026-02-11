from datetime import datetime
from typing import Generic, TypeVar, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

Lang = Literal["en", "vi"]

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

class TimestampMixin(BaseSchema):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

T = TypeVar("T")

class ApiResponse(BaseSchema, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None

class PaginationMeta(BaseSchema):
    page: int = 1
    page_size: int = 10
    total_items: int = 0
    total_pages: int = 0

class Page(BaseSchema, Generic[T]):
    items: List[T] = Field(default_factory=list)
    meta: PaginationMeta

class ErrorResponse(BaseSchema):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

class IDSchema(BaseSchema):
    id: int = Field(..., description="Primary ID")