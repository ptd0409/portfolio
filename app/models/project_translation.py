from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class ProjectTranslation(Base):
    __tablename__ = "project_translations"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    lang = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content_markdown = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint('project_id', 'lang'),)
    project = relationship("Project", back_populates="translations")