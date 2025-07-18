from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import re

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
        
        # 添加课程名称和教师真实姓名
        for exercise in exercises:
            exercise.course_name = exercise.course.name
            if exercise.course.teacher:
                exercise.teacher_name = exercise.course.teacher.real_name
            else:
                exercise.teacher_name = "未知教师"
        
        return exercises
    
    @staticmethod
    def get_teacher_exercises(db: Session, user_id: int, course_id: Optional[int] = None) -> List[Exercise]:
        """获取教师课程下的练习列表"""
        # 获取教师的课程ID列表
        teacher_courses = db.query(Course).filter(Course.teacher_id == user_id).all()
        course_ids = [course.id for course in teacher_courses]
        
        if not course_ids:
            return []
            
        # 查询条件：教师课程下的所有练习
        query = db.query(Exercise).filter(Exercise.course_id.in_(course_ids))
        
        # 如果指定了课程ID，进一步筛选
        if course_id:
            if course_id in course_ids:
                query = query.filter(Exercise.course_id == course_id)
            else:
                return []
        
        # 获取练习列表
        exercises = query.all()
        
        # 添加课程名称和教师真实姓名
        for exercise in exercises:
            exercise.course_name = exercise.course.name
            if exercise.course.teacher:
                exercise.teacher_name = exercise.course.teacher.real_name
            else:
                exercise.teacher_name = "未知教师"
        
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
        
        # 添加课程名称和教师真实姓名
        for exercise in exercises:
            exercise.course_name = exercise.course.name
            if exercise.course.teacher:
                exercise.teacher_name = exercise.course.teacher.real_name
            else:
                exercise.teacher_name = "未知教师"
        
        return exercises
    
    @staticmethod
    def get_exercise_detail(db: Session, exercise_id: int) -> Optional[Exercise]:
        """获取练习详情"""
        # 查询练习
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return None
        
        # 添加课程名称和教师真实姓名
        exercise.course_name = exercise.course.name
        if exercise.course.teacher:
            exercise.teacher_name = exercise.course.teacher.real_name
        else:
            exercise.teacher_name = "未知教师"
        
        return exercise
    
    @staticmethod
    def create_exercise(db: Session, user_id: int, name: str, course_id: int, end_time: Optional[datetime] = None,
                        is_online_judge: bool = True, note: Optional[str] = None, 
                        allowed_languages: str = "c", start_time: Optional[datetime] = None) -> Exercise:
        """创建练习"""
        # 创建练习
        new_exercise = Exercise(
            name=name,
            course_id=course_id,
            publisher_id=user_id,
            start_time=start_time if start_time else datetime.now(),
            end_time=end_time,
            is_online_judge=is_online_judge,
            note=note,
            allowed_languages=allowed_languages
        )
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        # 添加课程名称和教师真实姓名
        course = db.query(Course).filter(Course.id == course_id).first()
        new_exercise.course_name = course.name
        if course.teacher:
            new_exercise.teacher_name = course.teacher.real_name
        else:
            new_exercise.teacher_name = "未知教师"
        
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
        
        # 添加课程名称和教师真实姓名
        exercise.course_name = exercise.course.name
        if exercise.course.teacher:
            exercise.teacher_name = exercise.course.teacher.real_name
        else:
            exercise.teacher_name = "未知教师"
        
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
        
        # 检查教师是否是练习的发布者或课程的教师
        return exercise.publisher_id == user_id or exercise.course.teacher_id == user_id
    
    @staticmethod
    def log_operation(db: Session, user_id: int, operation: str, target: str) -> None:
        """记录操作日志"""
        log = OperationLog(
            user_id=user_id,
            operation=operation,
            target=target,
            created_at=datetime.now()  # 明确设置当前时间
        )
        db.add(log)
        db.commit()
        
    @staticmethod
    def add_problems_to_exercise(db: Session, exercise_id: int, user_id: int, problems_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """向练习添加题目"""
        # 查询练习
        exercise = ExerciseService.get_exercise_detail(db, exercise_id)
        if not exercise:
            raise ValueError("练习不存在")
        
        # 检查权限（教师只能更新自己发布的练习）
        if not ExerciseService.check_teacher_permission(db, user_id, exercise_id) and db.query(User).filter(User.id == user_id).first().role != "admin":
            raise ValueError("无权更新此练习")
        
        if not problems_data:
            raise ValueError("未提供题目数据")
        
        # 添加题目到练习
        problems_added = []
        problems_existing = []
        
        for problem_data in problems_data:
            try:
                # 检查必要字段
                if not problem_data.get("name"):
                    continue
                
                if not problem_data.get("data_path"):
                    continue
                
                # 确保data_path是字符串
                data_path = str(problem_data.get("data_path", ""))
                if not data_path:
                    continue
                
                # 处理time_limit - 安全地提取数字部分
                time_limit_str = str(problem_data.get("time_limit", "1000ms"))
                time_limit = 1000  # 默认值
                time_match = re.search(r'(\d+)', time_limit_str)
                if time_match:
                    time_limit = int(time_match.group(1))
                
                # 处理memory_limit - 安全地提取数字部分
                memory_limit_str = str(problem_data.get("memory_limit", "256MB"))
                memory_limit = 256  # 默认值（MB）
                memory_match = re.search(r'(\d+)', memory_limit_str)
                if memory_match:
                    memory_limit = int(memory_match.group(1))
                
                # 检查题目是否已存在
                existing_problem = db.query(Problem).filter(
                    Problem.data_path == data_path
                ).first()
                
                if existing_problem:
                    # 题目已存在，检查是否已添加到练习中
                    is_in_exercise = db.query(exercise_problem).filter(
                        exercise_problem.c.exercise_id == exercise_id,
                        exercise_problem.c.problem_id == existing_problem.id
                    ).first()
                    
                    if not is_in_exercise:
                        # 获取当前练习中的最大序号
                        max_sequence = db.query(exercise_problem.c.sequence).filter(
                            exercise_problem.c.exercise_id == exercise_id
                        ).order_by(exercise_problem.c.sequence.desc()).first()
                        
                        next_sequence = 1
                        if max_sequence:
                            next_sequence = max_sequence[0] + 1
                        
                        # 添加题目到练习
                        db.execute(
                            exercise_problem.insert().values(
                                exercise_id=exercise_id,
                                problem_id=existing_problem.id,
                                sequence=next_sequence
                            )
                        )
                        problems_added.append(existing_problem)
                    else:
                        # 题目已在练习中，记录下来
                        problems_existing.append(existing_problem)
                else:
                    # 创建新题目
                    new_problem = Problem(
                        name=problem_data.get("name"),
                        chinese_name=problem_data.get("chinese_name", problem_data.get("name")),
                        time_limit=time_limit,
                        memory_limit=memory_limit,
                        data_path=data_path,
                        category=problem_data.get("category", ""),
                        is_shared=True,
                        owner_id=user_id
                    )
                    db.add(new_problem)
                    db.flush()  # 获取新题目的ID
                    
                    # 获取当前练习中的最大序号
                    max_sequence = db.query(exercise_problem.c.sequence).filter(
                        exercise_problem.c.exercise_id == exercise_id
                    ).order_by(exercise_problem.c.sequence.desc()).first()
                    
                    next_sequence = 1
                    if max_sequence:
                        next_sequence = max_sequence[0] + 1
                    
                    # 添加题目到练习
                    db.execute(
                        exercise_problem.insert().values(
                            exercise_id=exercise_id,
                            problem_id=new_problem.id,
                            sequence=next_sequence
                        )
                    )
                    problems_added.append(new_problem)
            except Exception as e:
                continue  # 跳过这个题目，继续处理下一个
        
        if not problems_added and not problems_existing:
            db.rollback()
            raise ValueError("没有成功添加任何题目，请检查题目数据格式")
        
        db.commit()
        
        # 记录操作日志
        if problems_added:
            ExerciseService.log_operation(db, user_id, "添加题目", f"向练习 {exercise.name} 添加了 {len(problems_added)} 道题目")
        
        # 构建响应消息
        message = ""
        if problems_added:
            message += f"成功添加 {len(problems_added)} 道题目到练习。"
        if problems_existing:
            message += f"{len(problems_existing)} 道题目已在练习中。"
        
        return {
            "message": message.strip(),
            "added_count": len(problems_added),
            "existing_count": len(problems_existing)
        }
    
    @staticmethod
    def update_exercise_problem(db: Session, exercise_id: int, problem_id: int, user_id: int, problem_data: dict) -> dict:
        """更新练习中的题目"""
        # 查询练习
        exercise = ExerciseService.get_exercise_detail(db, exercise_id)
        if not exercise:
            raise ValueError("练习不存在")
        
        # 检查权限（教师只能更新自己发布的练习）
        if not ExerciseService.check_teacher_permission(db, user_id, exercise_id) and db.query(User).filter(User.id == user_id).first().role != "admin":
            raise ValueError("无权更新此练习")
        
        # 检查题目是否存在
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("题目不存在")
        
        # 检查题目是否属于练习
        problem_in_exercise = db.query(exercise_problem).filter(
            exercise_problem.c.exercise_id == exercise_id,
            exercise_problem.c.problem_id == problem_id
        ).first()
        
        if not problem_in_exercise:
            raise ValueError("题目不在练习中")
        
        # 更新题目
        for key, value in problem_data.items():
            if hasattr(problem, key):
                setattr(problem, key, value)
        
        db.commit()
        
        # 记录操作日志
        ExerciseService.log_operation(db, user_id, "更新题目", f"在练习 {exercise.name} 中更新题目 {problem.name}")
        
        return {"message": "题目更新成功"}
    
    @staticmethod
    def remove_problem_from_exercise(db: Session, exercise_id: int, problem_id: int, user_id: int) -> dict:
        """从练习中移除题目"""
        # 查询练习
        exercise = ExerciseService.get_exercise_detail(db, exercise_id)
        if not exercise:
            raise ValueError("练习不存在")
        
        # 检查权限（教师只能更新自己发布的练习）
        if not ExerciseService.check_teacher_permission(db, user_id, exercise_id) and db.query(User).filter(User.id == user_id).first().role != "admin":
            raise ValueError("无权更新此练习")
        
        # 检查题目是否存在于练习中
        problem_in_exercise = db.query(exercise_problem).filter(
            exercise_problem.c.exercise_id == exercise_id,
            exercise_problem.c.problem_id == problem_id
        ).first()
        
        if not problem_in_exercise:
            raise ValueError("题目不在练习中")
        
        # 获取题目信息用于日志
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        
        # 从练习中移除题目
        db.query(exercise_problem).filter(
            exercise_problem.c.exercise_id == exercise_id,
            exercise_problem.c.problem_id == problem_id
        ).delete()
        
        db.commit()
        
        # 记录操作日志
        problem_name = problem.name if problem else f"ID为{problem_id}的题目"
        ExerciseService.log_operation(db, user_id, "移除题目", f"从练习 {exercise.name} 中移除题目 {problem_name}")
        
        return {"message": "题目已从练习中移除"}
    
    @staticmethod
    def clear_exercise_problems(db: Session, exercise_id: int, user_id: int) -> dict:
        """清空练习中的所有题目"""
        # 查询练习
        exercise = ExerciseService.get_exercise_detail(db, exercise_id)
        if not exercise:
            raise ValueError("练习不存在")
        
        # 检查权限（教师只能更新自己发布的练习）
        if not ExerciseService.check_teacher_permission(db, user_id, exercise_id) and db.query(User).filter(User.id == user_id).first().role != "admin":
            raise ValueError("无权更新此练习")
        
        # 从练习中移除所有题目
        db.query(exercise_problem).filter(
            exercise_problem.c.exercise_id == exercise_id
        ).delete()
        
        db.commit()
        
        # 记录操作日志
        ExerciseService.log_operation(db, user_id, "清空题目", f"清空练习 {exercise.name} 中的所有题目")
        
        return {"message": "已清空练习中的所有题目"} 