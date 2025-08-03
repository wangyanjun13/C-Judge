from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base

# 问题-标签关联表
problem_tag = Table(
    'problem_tag',
    Base.metadata,
    Column('problem_id', Integer, ForeignKey('problems.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class TagType(Base):
    """标签类型模型"""
    __tablename__ = "tag_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    tags = relationship("Tag", back_populates="tag_type")


class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    tag_type_id = Column(Integer, ForeignKey("tag_types.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    tag_type = relationship("TagType", back_populates="tags")
    problems = relationship("Problem", secondary=problem_tag, back_populates="tags")

class TagApprovalRequest(Base):
    __tablename__ = "tag_approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_data_path = Column(String(255), nullable=False)
    requestor_id = Column(Integer, ForeignKey("users.id"))
    tag_ids = Column(JSONB, nullable=False)  # 存储标签ID数组
    status = Column(String(20), default='pending')  # 'pending', 'approved', 'rejected'
    request_message = Column(Text)  # 申请说明
    reviewer_id = Column(Integer, ForeignKey("users.id"))  # 审核者
    review_message = Column(Text)  # 审核说明
    created_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime)
    
    # 关系
    requestor = relationship("User", foreign_keys=[requestor_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id]) 