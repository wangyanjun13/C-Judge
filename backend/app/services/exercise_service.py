from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import User, Exercise, Course, Problem, OperationLog, Class, Submission
from app.models.exercise import exercise_problem

class ExerciseService:
    """练习服务类"""
    
    @staticmethod
    def get_student_exercises(db: Session, user_id: int, course_id: Optional[int] = None) -> List[Exercise]:
        """获取学生可见的练习列表"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.classes:
            return []
        
        # 获取学生所在班级的ID列表
        student_class_ids = [cls.id for cls in user.classes]
        
        # 查询条件：学生所在班级关联的课程的练习
        query = db.query(Exercise).join(Course).filter(
            Course.id.in_(
                db.query(Course.id)
                .join(Course.classes)
                .filter(Course.classes.any(Class.id.in_(student_class_ids)))
            )
        )
        
        # 如果指定了课程ID，进一步筛选
        if course_id:
            query = query.filter(Exercise.course_id == course_id)
        
        # 获取练习列表
        exercises = query.all()
        
        # 添加课程名称
        for exercise in exercises:
            exercise.course_name = exercise.course.name
        
        return exercises
    
    @staticmethod
    def get_teacher_exercises(db: Session, user_id: int, course_id: Optional[int] = None) -> List[Exercise]:
        """获取教师发布的练习列表"""
        # 查询条件：教师发布的练习
        query = db.query(Exercise).filter(Exercise.publisher_id == user_id)
        
        # 如果指定了课程ID，进一步筛选
        if course_id:
            query = query.filter(Exercise.course_id == course_id)
        
        # 获取练习列表
        exercises = query.all()
        
        # 添加课程名称
        for exercise in exercises:
            exercise.course_name = exercise.course.name
        
        return exercises
    
    @staticmethod
    def get_admin_exercises(db: Session, course_id: Optional[int] = None) -> List[Exercise]:
        """获取所有练习列表（管理员）"""
        # 查询条件
        query = db.query(Exercise)
        
        # 如果指定了课程ID，进一步筛选
        if course_id:
            query = query.filter(Exercise.course_id == course_id)
        
        # 获取练习列表
        exercises = query.all()
        
        # 添加课程名称
        for exercise in exercises:
            exercise.course_name = exercise.course.name
        
        return exercises
    
    @staticmethod
    def get_exercise_detail(db: Session, exercise_id: int) -> Optional[Exercise]:
        """获取练习详情"""
        # 查询练习
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return None
        
        # 添加课程名称
        exercise.course_name = exercise.course.name
        
        return exercise
    
    @staticmethod
    def create_exercise(db: Session, user_id: int, name: str, course_id: int, end_time: Optional[datetime] = None,
                        is_online_judge: bool = True, note: Optional[str] = None, 
                        allowed_languages: str = "c") -> Exercise:
        """创建练习"""
        # 创建练习
        new_exercise = Exercise(
            name=name,
            course_id=course_id,
            publisher_id=user_id,
            start_time=datetime.now(),
            end_time=end_time,
            is_online_judge=is_online_judge,
            note=note,
            allowed_languages=allowed_languages
        )
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        # 添加课程名称
        new_exercise.course_name = db.query(Course).filter(Course.id == course_id).first().name
        
        return new_exercise
    
    @staticmethod
    def update_exercise(db: Session, exercise_id: int, update_data: dict) -> Optional[Exercise]:
        """更新练习"""
        # 查询练习
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return None
        
        # 重命名字段
        if 'deadline' in update_data:
            update_data['end_time'] = update_data.pop('deadline')
        
        # 更新练习
        for key, value in update_data.items():
            setattr(exercise, key, value)
        
        db.commit()
        db.refresh(exercise)
        
        # 添加课程名称
        exercise.course_name = exercise.course.name
        
        return exercise
    
    @staticmethod
    def delete_exercise(db: Session, exercise_id: int) -> bool:
        """删除练习"""
        try:
            # 查询练习
            exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
            if not exercise:
                return False
            
            # 直接删除练习（让数据库级联处理关系）
            db.delete(exercise)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            print(f"删除练习失败: {str(e)}")
            return False
    
    @staticmethod
    def check_student_permission(db: Session, user_id: int, exercise_id: int) -> bool:
        """检查学生是否有权限查看练习"""
        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.classes:
            return False
        
        # 获取学生所在班级的ID列表
        student_class_ids = [cls.id for cls in user.classes]
        
        # 获取练习
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return False
        
        # 检查练习所属课程是否与学生班级关联
        course_classes = db.query(Course).filter(Course.id == exercise.course_id).first().classes
        return any(c.id in student_class_ids for c in course_classes)
    
    @staticmethod
    def check_teacher_permission(db: Session, user_id: int, exercise_id: int) -> bool:
        """检查教师是否有权限管理练习"""
        # 获取练习
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return False
        
        # 检查教师是否是练习的发布者
        return exercise.publisher_id == user_id
    
    @staticmethod
    def log_operation(db: Session, user_id: int, operation: str, target: str) -> None:
        """记录操作日志"""
        log = OperationLog(
            user_id=user_id,
            operation=operation,
            target=target
        )
        db.add(log)
        db.commit() 