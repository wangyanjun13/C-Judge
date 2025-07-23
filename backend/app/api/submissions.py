from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import desc, func
from sqlalchemy.sql import and_

from app.models.database import get_db
from app.models import Submission, User, Exercise, Problem, student_class, Class, Course
from app.models.course import course_class
from app.models.class_model import class_course
from app.schemas.submission import SubmissionCreate, SubmissionResponse, SubmissionDetail, ProblemRankingResponse
from app.schemas.submission import UserSubmissionResponse
from app.services.judge_service import JudgeService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/submissions", tags=["submissions"])

# 注意：这个路由必须放在 /{submission_id} 路由之前，否则会导致路径冲突
@router.get("/my-submissions", response_model=List[UserSubmissionResponse])
async def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, description="返回记录数量限制"),
    offset: int = Query(0, description="偏移量，用于分页"),
    sort: str = Query("desc", description="排序方式：asc（升序）或desc（降序）")
):
    """
    获取当前登录用户的所有答题记录，包括题目、练习、课程、班级名称
    """
    try:
        # 基本查询构建 - 获取用户答题记录并关联相关信息
        query = (
            db.query(
                Submission,
                Problem.name.label("problem_name"),
                Problem.chinese_name.label("problem_chinese_name"),
                Exercise.name.label("exercise_name"),
                Exercise.course_id,
                Course.name.label("course_name"),
            )
            .join(Problem, Submission.problem_id == Problem.id)
            .outerjoin(Exercise, Submission.exercise_id == Exercise.id)
            .outerjoin(Course, Exercise.course_id == Course.id)
            .filter(Submission.user_id == current_user.id)
        )
        
        # 按提交时间排序
        if sort.lower() == "asc":
            query = query.order_by(Submission.submitted_at.asc())
        else:
            query = query.order_by(Submission.submitted_at.desc())
        
        # 分页
        results = query.offset(offset).limit(limit).all()
        
        # 查询用户所在班级（用于补充班级信息）
        user_classes = {}
        if current_user.role == "student":
            classes = (
                db.query(Class)
                .join(student_class, Class.id == student_class.c.class_id)
                .filter(student_class.c.student_id == current_user.id)
                .all()
            )
            user_classes = {cls.id: cls.name for cls in classes}
        
        # 组装响应数据
        response_data = []
        
        for row in results:
            submission, problem_name, problem_chinese_name, exercise_name, course_id, course_name = row
            
            # 查询关联的班级信息
            class_names = []
            class_id = None
            
            if submission.exercise_id:
                # 获取该练习关联的班级
                try:
                    exercise_classes = (
                        db.query(Class)
                        .join(course_class, Class.id == course_class.c.class_id)
                        .join(Exercise, Exercise.course_id == course_class.c.course_id)
                        .filter(Exercise.id == submission.exercise_id)
                        .all()
                    )
                    
                    # 过滤出学生所在的班级
                    if current_user.role == "student" and user_classes:
                        filtered_classes = [cls for cls in exercise_classes if cls.id in user_classes]
                        if filtered_classes:
                            class_names = [cls.name for cls in filtered_classes]
                            class_id = filtered_classes[0].id
                        else:
                            class_names = [cls.name for cls in exercise_classes]
                            class_id = exercise_classes[0].id if exercise_classes else None
                    else:
                        class_names = [cls.name for cls in exercise_classes]
                        class_id = exercise_classes[0].id if exercise_classes else None
                except Exception as e:
                    print(f"查询练习关联班级出错: {str(e)}")
                    # 出错时使用默认值继续执行
                    class_names = []
                    class_id = None
            
            # 组装响应数据
            submission_data = {
                "id": submission.id,
                "user_id": submission.user_id,
                "problem_id": submission.problem_id,
                "exercise_id": submission.exercise_id,
                "language": submission.language,
                "status": submission.status,
                "code_check_score": submission.code_check_score,
                "runtime_score": submission.runtime_score,
                "total_score": submission.total_score,
                "submitted_at": submission.submitted_at,
                "problem_name": problem_name or f"题目 {submission.problem_id}",
                "problem_chinese_name": problem_chinese_name,
                "exercise_name": exercise_name or "-",
                "course_id": course_id,
                "course_name": course_name or "-",
                "class_names": ", ".join(class_names) if class_names else "-",
                "class_id": class_id
            }
            
            response_data.append(submission_data)
        
        return response_data
    except Exception as e:
        print(f"获取答题记录出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取答题记录失败: {str(e)}")

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

@router.get("/problem-ranking/{problem_id}", response_model=ProblemRankingResponse)
async def get_problem_ranking(
    problem_id: int,
    exercise_id: int = Query(..., description="练习ID"),
    class_id: Optional[int] = Query(None, description="班级ID，不传则查询所有班级"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题目在班级中的排名情况"""
    
    # 验证问题和练习是否存在
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    exercise = None
    if exercise_id:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="练习不存在")
    
    # 获取排名数据
    ranking_data = JudgeService.get_problem_ranking(
        db, problem_id, exercise_id, class_id, current_user.id
    )
    
    return ranking_data 