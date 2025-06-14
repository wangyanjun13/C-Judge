from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


# 练习-题目关联表
exercise_problem = Table(
    "exercise_problem",
    Base.metadata,
    Column("exercise_id", Integer, ForeignKey("exercises.id"), primary_key=True),
    Column("problem_id", Integer, ForeignKey("problems.id"), primary_key=True),
    Column("sequence", Integer, nullable=False)
)


class Exercise(Base):
    """练习模型"""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_online_judge = Column(Boolean, default=True)
    note = Column(Text, nullable=True)
    allowed_languages = Column(String, default="c")  # 逗号分隔的语言列表，如 "c,cpp,java"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", back_populates="exercises")
    
    publisher_id = Column(Integer, ForeignKey("users.id"))
    publisher = relationship("User", back_populates="published_exercises")
    
    problems = relationship("Problem", secondary=exercise_problem, back_populates="exercise")
    submissions = relationship("Submission", back_populates="exercise") 