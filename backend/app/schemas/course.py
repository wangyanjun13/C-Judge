from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    """课程基础模型"""
    name: str
    category: Optional[str] = None

class CourseCreate(CourseBase):
    """创建课程模型"""
    teacher_id: int
    class_ids: List[int]

class CourseUpdate(BaseModel):
    """更新课程模型"""
    name: Optional[str] = None
    category: Optional[str] = None
    teacher_id: Optional[int] = None
    class_ids: Optional[List[int]] = None

class TeacherInfo(BaseModel):
    """教师信息（简化版）"""
    id: int
    username: str
    real_name: Optional[str] = None

    class Config:
        orm_mode = True

class ClassInfo(BaseModel):
    """班级信息（简化版）"""
    id: int
    name: str

    class Config:
        orm_mode = True

class CourseResponse(CourseBase):
    """课程响应模型"""
    id: int
    teacher: TeacherInfo
    classes: List[ClassInfo]
    created_at: datetime

    class Config:
        orm_mode = True 