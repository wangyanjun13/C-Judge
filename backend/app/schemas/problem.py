from pydantic import BaseModel
from typing import List, Optional

class ProblemCategory(BaseModel):
    """题库分类模型"""
    name: str
    path: str

class ProblemInfo(BaseModel):
    """试题信息模型"""
    name: str
    chinese_name: str
    owner: str = "管理员"
    is_shared: bool = True
    time_limit: str
    memory_limit: str
    data_path: str
    category: str
    
class ProblemDelete(BaseModel):
    """试题删除响应模型"""
    message: str

class ProblemDetail(BaseModel):
    """试题详情响应模型"""
    id: int
    name: str
    chinese_name: Optional[str] = None
    time_limit: int = 1000
    memory_limit: int = 134217728
    html_content: Optional[str] = None
    data_path: Optional[str] = None
    category: Optional[str] = None
    code_check_score: int = 20
    runtime_score: int = 80
    score_method: str = "sum"

    class Config:
        orm_mode = True 