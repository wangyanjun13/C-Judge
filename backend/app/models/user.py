from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    real_name = Column(String)
    role = Column(String, nullable=False)  # 'student', 'teacher', 'admin'
    is_online = Column(Boolean, default=False)  # 数据库中是 is_online 而不是 is_active
    register_time = Column(DateTime, server_default=func.now())  # 数据库中是 register_time 而不是 created_at
    # 数据库中没有 last_login 字段，暂时注释掉
    # last_login = Column(DateTime(timezone=True), nullable=True)

    # 关系
    submissions = relationship("Submission", back_populates="user")
    published_exercises = relationship("Exercise", back_populates="publisher")
    operation_logs = relationship("OperationLog", back_populates="user")
    
    # 教师关系
    courses = relationship("Course", back_populates="teacher")
    teaching_classes = relationship(
        "Class",
        secondary="teacher_class",
        back_populates="teachers"
    )
    
    # 学生关系 - 通过 student_class 关联表关联到 classes
    # 数据库中没有 class_id 字段，使用多对多关系
    # class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    # class_relation = relationship("Class", back_populates="students")
    
    # 学生关系
    classes = relationship(
        "Class",
        secondary="student_class",
        back_populates="students"
    ) 