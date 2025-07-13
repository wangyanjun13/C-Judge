from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base

# 创建问题-标签关联表
problem_tag = Table(
    "problem_tag",
    Base.metadata,
    Column("problem_id", Integer, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class TagType(Base):
    """标签类型模型"""
    __tablename__ = "tag_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    tags = relationship("Tag", back_populates="tag_type")


class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tag_type_id = Column(Integer, ForeignKey("tag_types.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    tag_type = relationship("TagType", back_populates="tags")
    problems = relationship("Problem", secondary=problem_tag, back_populates="tags") 