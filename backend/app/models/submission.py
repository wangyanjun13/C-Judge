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
    status = Column(String, nullable=True)  # 'Pending', 'Accepted', 'Wrong Answer', 'Compilation Error', etc.
    code_check_score = Column(Integer, nullable=True)
    runtime_score = Column(Integer, nullable=True)
    total_score = Column(Integer, nullable=True)
    result = Column(JSONB, nullable=True)  # 评测结果详情
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions") 