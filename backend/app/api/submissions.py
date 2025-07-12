from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.database import get_db
from app.models import Submission, User, Exercise, Problem
from app.schemas.submission import SubmissionCreate, SubmissionResponse, SubmissionDetail
from app.services.judge_service import JudgeService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.post("/", response_model=SubmissionResponse)
async def submit_code(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交代码进行评测
    """
    # 检查用户权限（学生只能提交自己的代码）
    if current_user.role == "student" and submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您只能提交自己的代码"
        )

    # 检查练习是否存在
    if submission.exercise_id:
        exercise = db.query(Exercise).filter(Exercise.id == submission.exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="练习不存在"
            )
        
        # 检查练习是否已开始
        now = datetime.now().replace(tzinfo=None)
        if exercise.start_time and now < exercise.start_time.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="练习尚未开始，无法提交"
            )
        
        # 检查练习是否已截止
        if exercise.end_time and now > exercise.end_time.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="练习已截止，无法提交"
            )

    # 检查题目是否存在
    problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    try:
        # 使用评测服务进行提交
        result = JudgeService.submit(
            db=db,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            exercise_id=submission.exercise_id,
            code=submission.code,
            language=submission.language
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")

@router.get("/{submission_id}", response_model=SubmissionDetail)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取提交记录详情
    """
    # 查询提交记录
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    # 检查记录是否存在
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    # 检查权限（学生只能查看自己的提交）
    if current_user.role == "student" and submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看其他用户的提交记录"
        )
    
    # 获取测试用例数据
    try:
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        if problem and problem.data_path:
            test_cases = JudgeService.get_test_cases(problem.data_path)
            submission.test_cases = test_cases
    except Exception as e:
        print(f"获取测试用例数据失败: {e}")
        submission.test_cases = None
    
    return submission

@router.get("/", response_model=List[SubmissionResponse])
async def get_submissions(
    user_id: Optional[int] = None,
    problem_id: Optional[int] = None,
    exercise_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取提交记录列表
    可以按用户ID、问题ID或练习ID筛选
    """
    # 构造查询
    query = db.query(Submission)
    
    # 应用筛选条件
    if user_id is not None:
        # 检查权限（学生只能查看自己的提交）
        if current_user.role == "student" and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看其他用户的提交记录"
            )
        query = query.filter(Submission.user_id == user_id)
    
    if problem_id is not None:
        query = query.filter(Submission.problem_id == problem_id)
    
    if exercise_id is not None:
        query = query.filter(Submission.exercise_id == exercise_id)
    
    # 对于学生，只显示自己的提交
    if current_user.role == "student":
        query = query.filter(Submission.user_id == current_user.id)
    
    # 按提交时间降序排序
    submissions = query.order_by(Submission.submitted_at.desc()).all()
    
    return submissions 