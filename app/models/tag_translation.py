from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class TagTranslation(Base):
    __tablename__ = "tag_translations"
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    lang = Column(String, nullable=False)
    name = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint('tag_id', 'lang'),)
    tag = relationship("Tag", back_populates="tag_translations")