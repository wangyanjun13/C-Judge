from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

# 提交代码请求模型
class SubmissionCreate(BaseModel):
    user_id: int
    problem_id: int
    exercise_id: Optional[int] = None
    code: str
    language: str = "c"

# 提交响应模型
class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    exercise_id: Optional[int] = None
    language: str
    status: str
    code_check_score: Optional[int] = None
    runtime_score: Optional[int] = None
    total_score: Optional[int] = None
    submitted_at: datetime

    class Config:
        orm_mode = True

# 提交详情响应模型
class SubmissionDetail(SubmissionResponse):
    code: str
    result: Optional[Dict[str, Any]] = None
    test_cases: Optional[List[Dict[str, Any]]] = None

    class Config:
        orm_mode = True

# 提交记录列表请求参数
class SubmissionFilter(BaseModel):
    user_id: Optional[int] = None
    problem_id: Optional[int] = None
    exercise_id: Optional[int] = None
    status: Optional[str] = None 

class SubmissionRank(BaseModel):
    user_id: int
    username: str
    real_name: Optional[str] = None
    score: Optional[int] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProblemRankingResponse(BaseModel):
    rankings: List[SubmissionRank]
    current_user_rank: Optional[int] = None
    total_students: int
    submission_count: int
    
    class Config:
        orm_mode = True 

# 用户提交记录响应模型（包含额外的题目、练习、课程、班级名称）
class UserSubmissionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    exercise_id: Optional[int] = None
    language: str
    status: str
    code_check_score: Optional[int] = None
    runtime_score: Optional[int] = None
    total_score: Optional[int] = None
    submitted_at: datetime
    problem_name: str
    problem_chinese_name: Optional[str] = None
    exercise_name: Optional[str] = None
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    class_names: Optional[str] = None
    class_id: Optional[int] = None
    username: str
    real_name: Optional[str] = None
    
    class Config:
        orm_mode = True 