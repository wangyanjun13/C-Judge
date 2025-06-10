from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import User, Exercise, Course, Problem, get_db, OperationLog, Class
from app.models.exercise import exercise_problem
from app.utils.auth import get_current_active_user, get_teacher_user, get_admin_user
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取练习详情"""
    # 查询练习
    exercise = ExerciseService.get_exercise_detail(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="练习不存在")
    
    # 检查权限
    if current_user.role == "student":
        # 学生只能查看自己班级关联课程的练习
        if not ExerciseService.check_student_permission(db, current_user.id, exercise_id):
            raise HTTPException(status_code=403, detail="无权查看此练习")
    elif current_user.role == "teacher" and not ExerciseService.check_teacher_permission(db, current_user.id, exercise_id):
        # 教师只能查看自己发布的练习
        raise HTTPException(status_code=403, detail="无权查看此练习")
    
    # 记录操作日志
    ExerciseService.log_operation(db, current_user.id, "查看练习详情", exercise.name)
    
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
    
    # 创建练习
    exercise = ExerciseService.create_exercise(
        db,
        current_user.id,
        exercise_data.name,
        exercise_data.course_id,
        exercise_data.end_time,
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
        raise HTTPException(status_code=500, detail="删除练习失败")
    
    return {"message": "练习删除成功"} 