from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
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
    input: str = ""  # 允许为空字符串
    output: str = ""  # 允许为空字符串

class CustomProblemCreate(BaseModel):
    """自定义题目创建模型"""
    name: str
    chinese_name: str
    description: str
    testcases: List[TestCase]
    tag_ids: Optional[List[int]] = []  # 可选的标签ID列表
    reference_answer: Optional[str] = None  # 新增：参考答案（可为空）

class CustomProblemResponse(BaseModel):
    """自定义题目创建响应模型"""
    success: bool
    message: str
    problem_path: Optional[str] = None

# 收藏相关Schema
class FavoriteRequest(BaseModel):
    """添加收藏请求"""
    problem_id: int

class FavoriteResponse(BaseModel):
    """收藏操作响应"""
    success: bool
    message: str
    is_favorited: Optional[bool] = None

class FavoriteProblemInfo(BaseModel):
    """收藏的题目信息"""
    id: int
    name: str
    chinese_name: Optional[str] = None
    data_path: Optional[str] = None
    category: Optional[str] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    favorited_at: datetime
    
    class Config:
        from_attributes = True

class UserFavoritesResponse(BaseModel):
    """用户收藏列表响应"""
    total: int
    favorites: List[FavoriteProblemInfo]

class FavoriteStatusResponse(BaseModel):
    """收藏状态响应"""
    is_favorited: bool
    favorite_count: int 