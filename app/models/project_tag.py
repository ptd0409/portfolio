from app.db.base import Base
from sqlalchemy import Table, Column, Integer, ForeignKey

class ProjectTag(Base):
    __tablename__ = "project_tags"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)