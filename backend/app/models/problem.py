from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base
from .exercise import exercise_problem


class Problem(Base):
    """问题模型"""
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 英文名称
    chinese_name = Column(String, nullable=False)  # 中文名称
    description = Column(Text, nullable=True)
    time_limit = Column(Integer, default=1000)  # 毫秒
    memory_limit = Column(Integer, default=256)  # MB
    code_review_score = Column(Float, default=0)
    runtime_score = Column(Float, default=100)
    score_method = Column(String, default="sum")  # sum或max
    test_case_path = Column(String, nullable=True)
    
    # 关系
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    exercise = relationship("Exercise", back_populates="problems")
    
    category_id = Column(Integer, ForeignKey("problem_categories.id"), nullable=True)
    category = relationship("ProblemCategory", back_populates="problems")
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User")
    
    submissions = relationship("Submission", back_populates="problem")

class ProblemCategory(Base):
    """问题分类模型"""
    __tablename__ = "problem_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    # 关系
    problems = relationship("Problem", back_populates="category") 