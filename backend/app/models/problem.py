from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base
from .exercise import exercise_problem


class Problem(Base):
    """问题模型"""
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 英文名称
    chinese_name = Column(String, nullable=True)  # 中文名称
    time_limit = Column(Integer, default=1000)  # 毫秒
    memory_limit = Column(Integer, default=134217728)  # bytes (128MB)
    code_check_score = Column(Integer, default=0)
    runtime_score = Column(Integer, default=100)
    score_method = Column(String, default="sum")  # sum或max
    data_path = Column(String, nullable=True)
    category = Column(String, nullable=True)
    is_shared = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User")
    
    # 使用secondary定义多对多关系
    exercise = relationship("Exercise", secondary=exercise_problem, back_populates="problems")
    submissions = relationship("Submission", back_populates="problem")

# 保留ProblemCategory类，但修复与Problem的关系
class ProblemCategory(Base):
    """问题分类模型"""
    __tablename__ = "problem_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    # 修复关系定义，使用外部显式定义而不是back_populates
    problems = relationship("Problem", 
                           primaryjoin="and_(Problem.category==ProblemCategory.name)",
                           foreign_keys=[Problem.category],
                           viewonly=True) 