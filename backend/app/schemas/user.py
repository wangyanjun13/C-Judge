from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.schemas.class_schema import ClassResponse

# 基础用户模型
class UserBase(BaseModel):
    username: str
    real_name: Optional[str] = None

# 创建用户请求
class UserCreate(UserBase):
    password: str
    role: str = "student"

# 更新用户请求
class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    password: Optional[str] = None

# 用户登录请求
class UserLogin(BaseModel):
    username: str
    password: str

# 用户响应模型
class UserResponse(UserBase):
    id: int
    role: str
    is_online: bool
    register_time: datetime

    class Config:
        orm_mode = True

# 令牌响应
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# 教师响应模型
class TeacherResponse(UserResponse):
    pass

# 班级信息模型（简化版）
class ClassInfo(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# 学生响应模型
class StudentResponse(UserResponse):
    classes: List[ClassInfo] = []

    class Config:
        orm_mode = True

# 批量导入学生请求
class BatchStudentImport(BaseModel):
    students: List[dict]  # 格式：[{"username": "...", "password": "...", "real_name": "..."}]
    class_id: int 