from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base
from app.models.class_model import class_course


# 课程-班级关联表
course_class = Table(
    "course_class",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("class_id", Integer, ForeignKey("classes.id"), primary_key=True)
)


class Course(Base):
    """课程模型"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # 课程类别
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    teacher_id = Column(Integer, ForeignKey("users.id"))
    teacher = relationship("User", back_populates="courses")
    
    classes = relationship("Class", secondary=class_course, back_populates="courses")
    exercises = relationship("Exercise", back_populates="course") 