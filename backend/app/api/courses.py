from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import User, Course, Class, get_db, OperationLog
from app.utils.auth import get_current_active_user, get_teacher_user, get_admin_user
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.services import CourseService, UserService

router = APIRouter(prefix="/courses", tags=["课程"])

@router.get("/test")
async def test_courses_api():
    """测试课程API，无需身份验证"""
    return {"status": "ok", "message": "课程API工作正常"}

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取课程列表"""
    # 记录操作日志
    CourseService.log_operation(db, current_user.id, "查看课程列表", "课程列表")
    
    # 获取课程列表
    return CourseService.get_courses(db, current_user.id)

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """创建课程（教师或管理员）"""
    # 如果不是管理员，只能为自己创建课程
    if current_user.role != "admin" and course_data.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能为自己创建课程")
    
    # 如果是管理员，检查教师是否存在
    if current_user.role == "admin":
        teacher = db.query(User).filter(
            User.id == course_data.teacher_id,
            User.role == "teacher"
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
    
    # 创建课程
    new_course = CourseService.create_course(
        db, 
        course_data.name, 
        course_data.teacher_id, 
        course_data.category, 
        course_data.class_ids
    )
    
    if not new_course:
        raise HTTPException(status_code=404, detail="创建课程失败，请检查班级是否存在")
    
    # 记录操作日志
    CourseService.log_operation(db, current_user.id, "创建课程", new_course.name)
    
    return new_course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """更新课程（教师或管理员）"""
    # 查询课程
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查权限
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能更新自己的课程")
    
    # 更新课程
    update_data = course_data.dict(exclude_unset=True)
    updated_course = CourseService.update_course(db, course_id, update_data)
    
    if not updated_course:
        raise HTTPException(status_code=404, detail="更新课程失败，请检查教师或班级是否存在")
    
    # 记录操作日志
    CourseService.log_operation(db, current_user.id, "更新课程", updated_course.name)
    
    return updated_course

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """删除课程（教师或管理员）"""
    # 查询课程
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查权限
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的课程")
    
    # 记录操作日志
    CourseService.log_operation(db, current_user.id, "删除课程", course.name)
    
    # 删除课程
    success = CourseService.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=400, detail="课程有关联的练习，请先删除这些练习")
    
    return {"message": "课程删除成功"} 