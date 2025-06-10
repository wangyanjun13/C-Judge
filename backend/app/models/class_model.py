from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


# 学生-班级关联表
student_class = Table(
    "student_class",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("class_id", Integer, ForeignKey("classes.id"), primary_key=True)
)

# 班级与课程的多对多关系
class_course = Table(
    "class_course",
    Base.metadata,
    Column("class_id", Integer, ForeignKey("classes.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    students = relationship(
        "User",
        secondary=student_class,
        back_populates="classes"
    )
    courses = relationship(
        "Course",
        secondary=class_course,
        back_populates="classes"
    ) 