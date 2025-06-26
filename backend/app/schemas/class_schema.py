from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TeacherInfo(BaseModel):
    """教师信息模型"""
    id: int
    username: str
    real_name: str

    class Config:
        orm_mode = True

class ClassBase(BaseModel):
    """班级基础模型"""
    name: str
    
class ClassCreate(ClassBase):
    """创建班级模型"""
    teacher_ids: List[int]

class ClassUpdate(ClassBase):
    """更新班级模型"""
    teacher_ids: List[int]

class ClassResponse(ClassBase):
    """班级响应模型"""
    id: int
    created_at: datetime
    student_count: int
    teachers: List[TeacherInfo]
    
    class Config:
        orm_mode = True 