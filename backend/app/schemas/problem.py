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