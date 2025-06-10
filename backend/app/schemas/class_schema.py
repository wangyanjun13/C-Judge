from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClassBase(BaseModel):
    """班级基础模型"""
    name: str
    
class ClassCreate(ClassBase):
    """创建班级模型"""
    pass

class ClassUpdate(ClassBase):
    """更新班级模型"""
    pass

class ClassResponse(ClassBase):
    """班级响应模型"""
    id: int
    created_at: datetime
    student_count: int
    
    class Config:
        orm_mode = True 