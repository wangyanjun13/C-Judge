from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime

# 问题简要信息
class ProblemBrief(BaseModel):
    id: int
    name: str
    chinese_name: Optional[str] = None
    time_limit: int
    memory_limit: int
    code_check_score: int = 0
    runtime_score: int = 100
    score_method: str = "sum"
    category: Optional[str] = None
    data_path: Optional[str] = None

    class Config:
        orm_mode = True

# 创建练习请求
class ExerciseCreate(BaseModel):
    name: str
    course_id: int
    end_time: Optional[datetime] = None
    is_online_judge: bool = True
    note: Optional[str] = None
    allowed_languages: str = "c"

# 更新练习请求
class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    end_time: Optional[datetime] = None
    is_online_judge: Optional[bool] = None
    note: Optional[str] = None
    allowed_languages: Optional[str] = None

# 练习响应
class ExerciseResponse(BaseModel):
    id: int
    name: str
    course_id: int
    course_name: str = ""  # 在API中动态添加
    publisher_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_online_judge: bool
    note: Optional[str] = None
    allowed_languages: str
    created_at: datetime

    class Config:
        orm_mode = True

# 练习详情响应
class ExerciseDetailResponse(ExerciseResponse):
    problems: List[ProblemBrief] = []  # 在API中动态添加

    class Config:
        orm_mode = True 