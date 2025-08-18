from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tag import Tag

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
    tags: List[Tag] = []
    
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
    tags: List[Tag] = []

    class Config:
        orm_mode = True 

class TestCase(BaseModel):
    """测试用例模型"""
    input: str
    output: str

class CustomProblemCreate(BaseModel):
    """自定义题目创建模型"""
    name: str
    chinese_name: str
    description: str
    testcases: List[TestCase]
    tag_ids: Optional[List[int]] = []  # 可选的标签ID列表

class CustomProblemResponse(BaseModel):
    """自定义题目创建响应模型"""
    success: bool
    message: str
    problem_path: Optional[str] = None 