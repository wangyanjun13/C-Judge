from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models import User, Exercise, Course, Problem, get_db, OperationLog, Class, Submission
from app.models.exercise import exercise_problem
from app.utils.auth import get_current_active_user, get_current_user, get_teacher_user, get_admin_user
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse, ExerciseDetailResponse
from app.services import ExerciseService

router = APIRouter(prefix="/exercises", tags=["练习"])

@router.get("/student", response_model=List[ExerciseResponse])
async def get_student_exercises(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学生可见的练习列表"""
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "查看练习列表", "练习列表")
    
    # 获取练习列表
    exercises = ExerciseService.get_student_exercises(db, current_user.id, course_id)
    
    # 调试输出
    print("学生练习列表:")
    for ex in exercises:
        print(f"ID: {ex.id}, 名称: {ex.name}, 课程: {ex.course_name}, 教师: {getattr(ex, 'teacher_name', '无')}")
    
    return exercises

@router.get("/teacher", response_model=List[ExerciseResponse])
async def get_teacher_exercises(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """获取教师发布的练习列表"""
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "查看练习列表", "练习列表")
    
    # 获取练习列表
    exercises = ExerciseService.get_teacher_exercises(db, current_user.id, course_id)
    
    return exercises

@router.get("/admin", response_model=List[ExerciseResponse])
async def get_admin_exercises(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取所有练习列表（管理员）"""
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "查看练习列表", "练习列表")
    
    # 获取练习列表
    exercises = ExerciseService.get_admin_exercises(db, course_id)
    
    return exercises

@router.get("/{exercise_id}", response_model=ExerciseDetailResponse)
async def get_exercise_detail(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """获取练习详情"""
    # 简化逻辑，直接查询练习
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="练习不存在")
    
    # 确保problems属性存在
    if not hasattr(exercise, 'problems'):
        exercise.problems = []
    
    return exercise

@router.post("/", response_model=ExerciseResponse)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """创建练习（教师或管理员）"""
    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == exercise_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查权限（教师只能为自己的课程创建练习）
    if current_user.role == "teacher" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权为此课程创建练习")
    
    # 确保end_time字段有值，如果为None，设置为当前时间一年后
    end_time = exercise_data.end_time
    if not end_time:
        end_time = datetime.now() + timedelta(days=365)  # 默认一年后截止
    
    # 创建练习
    exercise = ExerciseService.create_exercise(
        db,
        current_user.id,
        exercise_data.name,
        exercise_data.course_id,
        end_time,
        exercise_data.is_online_judge,
        exercise_data.note,
        exercise_data.allowed_languages
    )
    
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "创建练习", exercise.name)
    
    return exercise

@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """更新练习（教师或管理员）"""
    # 查询练习
    exercise = ExerciseService.get_exercise_detail(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="练习不存在")
    
    # 检查权限（教师只能更新自己发布的练习）
    if current_user.role == "teacher" and not ExerciseService.check_teacher_permission(db, current_user.id, exercise_id):
        raise HTTPException(status_code=403, detail="无权更新此练习")
    
    # 更新练习
    update_data = exercise_data.dict(exclude_unset=True)
    
    # 确保end_time有值且晚于start_time
    if "end_time" in update_data and update_data["end_time"]:
        print(f"更新练习 {exercise_id} 的截止时间为: {update_data['end_time']}")
    else:
        print(f"未提供截止时间或截止时间为空")
    
    updated_exercise = ExerciseService.update_exercise(db, exercise_id, update_data)
    
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "更新练习", updated_exercise.name)
    
    return updated_exercise

@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """删除练习（教师或管理员）"""
    try:
        # 查询练习
        exercise = ExerciseService.get_exercise_detail(db, exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="练习不存在")
        
        # 检查权限（教师只能删除自己发布的练习）
        if current_user.role == "teacher" and not ExerciseService.check_teacher_permission(db, current_user.id, exercise_id):
            raise HTTPException(status_code=403, detail="无权删除此练习")
        
        # 记录操作日志
        ExerciseService.log_operation(db, current_user.id, "删除练习", exercise.name)
        
        # 删除练习
        success = ExerciseService.delete_exercise(db, exercise_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除练习失败，可能存在关联数据")
        
        return {"message": "练习删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除练习时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除练习失败: {str(e)}")

@router.post("/{exercise_id}/problems")
async def add_problems_to_exercise(
    exercise_id: int,
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """向练习添加题目（教师或管理员）"""
    try:
        # 解析请求数据
        problems_data = data.get("problems", [])
        
        print(f"API接收到的数据: {data}")
        print(f"解析出的题目数据: {problems_data}")
        
        if not problems_data:
            raise ValueError("未提供题目数据")
        
        # 调用服务层方法添加题目
        result = ExerciseService.add_problems_to_exercise(
            db=db,
            exercise_id=exercise_id,
            user_id=current_user.id,
            problems_data=problems_data
        )
        
        return result
    except ValueError as e:
        # 将服务层的ValueError转换为HTTP异常
        print(f"添加题目失败(值错误): {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"添加题目失败(未知错误): {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加题目失败: {str(e)}")

@router.put("/{exercise_id}/problems/{problem_id}")
async def update_exercise_problem(
    exercise_id: int,
    problem_id: int,
    problem_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """更新练习中的题目（教师或管理员）"""
    try:
        result = ExerciseService.update_exercise_problem(
            db=db,
            exercise_id=exercise_id,
            problem_id=problem_id,
            user_id=current_user.id,
            problem_data=problem_data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新题目失败: {str(e)}")

@router.delete("/{exercise_id}/problems/{problem_id}")
async def remove_problem_from_exercise(
    exercise_id: int,
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """从练习中移除题目（教师或管理员）"""
    try:
        result = ExerciseService.remove_problem_from_exercise(
            db=db,
            exercise_id=exercise_id,
            problem_id=problem_id,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"移除题目失败: {str(e)}")

@router.delete("/{exercise_id}/problems")
async def clear_exercise_problems(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """清空练习中的所有题目（教师或管理员）"""
    try:
        result = ExerciseService.clear_exercise_problems(
            db=db,
            exercise_id=exercise_id,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空题目失败: {str(e)}")

@router.get("/{exercise_id}/statistics", response_model=Dict[str, Any])
async def get_exercise_statistics(
    exercise_id: int,
    class_id: Optional[int] = None,
    include_special_users: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取练习的答题统计数据
    如果提供了class_id，则只返回该班级学生的统计数据
    否则返回与该练习关联的所有班级学生的统计数据
    如果include_special_users为True，则包含管理员和教师的答题情况
    """
    try:
        # 检查用户权限
        if current_user.role not in ['admin', 'teacher']:
            raise HTTPException(
                status_code=403,
                detail="只有管理员和教师可以查看答题统计"
            )
            
        # 获取练习详情
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=404,
                detail="练习不存在"
            )
            
        # 获取练习的所有题目
        problems = exercise.problems
        if not problems:
            return {
                "exercise_name": exercise.name,
                "problems": [],
                "students": [],
                "statistics": []
            }
            
        # 获取与该练习关联的班级
        course = exercise.course
        if not course:
            raise HTTPException(
                status_code=404,
                detail="练习未关联课程"
            )
            
        classes = course.classes
        if class_id:
            # 如果指定了班级，则只返回该班级的数据
            classes = [cls for cls in classes if cls.id == class_id]
            if not classes:
                raise HTTPException(
                    status_code=404,
                    detail="未找到指定班级或该班级未关联此课程"
                )
                
        # 获取所有相关学生
        students = []
        for cls in classes:
            students.extend(cls.students)
            
        # 去重
        students = list({student.id: student for student in students}.values())
        
        # 获取所有学生在所有题目上的提交记录
        statistics = []
        
        # 如果需要包含管理员和教师的答题情况
        if include_special_users:
            # 获取管理员
            admins = db.query(User).filter(User.role == 'admin').all()
            
            # 获取课程关联的教师
            teacher = course.teacher
            
            # 合并特殊用户（管理员和教师）
            special_users = []
            if admins:
                special_users.extend(admins)
            if teacher and teacher not in special_users:
                special_users.append(teacher)
                
            # 获取特殊用户的答题情况
            for user in special_users:
                user_stats = {
                    "user_id": user.id,
                    "username": user.username,
                    "real_name": user.real_name or user.username,
                    "role": user.role,
                    "total_score": 0,
                    "problem_scores": {}
                }
                
                # 获取该用户在该练习中的所有提交记录
                submissions = db.query(Submission).filter(
                    Submission.user_id == user.id,
                    Submission.exercise_id == exercise_id
                ).all()
                
                # 为每个题目找到最高分的提交
                for problem in problems:
                    problem_submissions = [s for s in submissions if s.problem_id == problem.id]
                    if problem_submissions:
                        # 取最高分的提交
                        best_submission = max(problem_submissions, key=lambda s: s.total_score or 0)
                        user_stats["problem_scores"][problem.id] = {
                            "score": best_submission.total_score or 0,
                            "submission_id": best_submission.id,
                            "status": best_submission.status
                        }
                        user_stats["total_score"] += best_submission.total_score or 0
                    else:
                        user_stats["problem_scores"][problem.id] = {
                            "score": None,
                            "submission_id": None,
                            "status": "未提交"
                        }
                
                statistics.append(user_stats)
        
        # 添加学生统计数据
        for student in students:
            student_stats = {
                "student_id": student.id,
                "username": student.username,
                "real_name": student.real_name or student.username,
                "class_names": [cls.name for cls in student.classes],
                "total_score": 0,
                "problem_scores": {}
            }
            
            # 获取该学生在该练习中的所有提交记录
            submissions = db.query(Submission).filter(
                Submission.user_id == student.id,
                Submission.exercise_id == exercise_id
            ).all()
            
            # 为每个题目找到最高分的提交
            for problem in problems:
                problem_submissions = [s for s in submissions if s.problem_id == problem.id]
                if problem_submissions:
                    # 取最高分的提交
                    best_submission = max(problem_submissions, key=lambda s: s.total_score or 0)
                    student_stats["problem_scores"][problem.id] = {
                        "score": best_submission.total_score or 0,
                        "submission_id": best_submission.id,
                        "status": best_submission.status
                    }
                    student_stats["total_score"] += best_submission.total_score or 0
                else:
                    student_stats["problem_scores"][problem.id] = {
                        "score": None,
                        "submission_id": None,
                        "status": "未提交"
                    }
            
            statistics.append(student_stats)
        
        # 按总分排序
        statistics.sort(key=lambda x: x["total_score"], reverse=True)
        
        # 添加序号（只为学生添加序号）
        rank = 1
        for stat in statistics:
            if "student_id" in stat:  # 只为学生添加排名
                stat["rank"] = rank
                rank += 1
        
        # 构造返回数据
        result = {
            "exercise_name": exercise.name,
            "problems": [
                {
                    "id": p.id,
                    "name": p.name,
                    "chinese_name": p.chinese_name,
                    "code_check_score": p.code_check_score,
                    "runtime_score": p.runtime_score,
                    "total_score": p.code_check_score + p.runtime_score
                } for p in problems
            ],
            "classes": [
                {
                    "id": cls.id,
                    "name": cls.name
                } for cls in classes
            ],
            "statistics": statistics
        }
        
        # 如果是管理员，添加课程教师信息
        if current_user.role == 'admin' and course.teacher:
            result["course_teacher"] = {
                "id": course.teacher.id,
                "username": course.teacher.username,
                "real_name": course.teacher.real_name
            }
        
        return result
        
    except Exception as e:
        # 记录错误
        print(f"获取练习统计数据出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        ) 