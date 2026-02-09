from app.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    tag_translations = relationship("TagTranslation", back_populates="tag")
    projects = relationship("Project", secondary="project_tags", back_populates="tags")