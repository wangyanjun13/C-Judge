from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base


class Submission(Base):
    """提交模型"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 'Pending', 'Accepted', 'Wrong Answer', 'Compilation Error', etc.
    score = Column(Float, default=0)
    code_review_score = Column(Float, default=0)
    runtime_score = Column(Float, default=0)
    time_used = Column(Integer, nullable=True)  # 毫秒
    memory_used = Column(Integer, nullable=True)  # MB
    error_message = Column(Text, nullable=True)
    result = Column(JSONB)  # 评测结果详情
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions") 