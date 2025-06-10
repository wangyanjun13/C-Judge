import os
import sys
from sqlalchemy.orm import Session

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal, Base, engine
from app.models import User, SystemSetting, Class, Course
from app.utils.auth import get_password_hash

def init_db():
    """初始化数据库"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            # 创建管理员用户
            admin_user = User(
                username="admin",
                password=get_password_hash("admin"),
                real_name="系统管理员",
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("已创建管理员用户: admin/admin")
            
            # 创建示例教师用户
            teacher_user = User(
                username="teacher",
                password=get_password_hash("teacher"),
                real_name="示例教师",
                role="teacher"
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)
            print("已创建教师用户: teacher/teacher")
            
            # 创建示例班级
            demo_class = Class(name="示例班级")
            db.add(demo_class)
            db.commit()
            db.refresh(demo_class)
            print(f"已创建示例班级: {demo_class.name}")
            
            # 创建示例学生用户
            student_user = User(
                username="student",
                password=get_password_hash("student"),
                real_name="示例学生",
                role="student",
                class_id=demo_class.id
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)
            print("已创建学生用户: student/student")
            
            # 创建示例课程
            demo_course = Course(
                name="C语言程序设计",
                category="编程基础",
                teacher_id=teacher_user.id
            )
            db.add(demo_course)
            db.commit()
            db.refresh(demo_course)
            print(f"已创建示例课程: {demo_course.name}")
        
        # 初始化系统设置
        settings = [
            {"key": "page_size", "value": "10", "description": "表格每页显示行数"},
            {"key": "default_code_check_score", "value": "0", "description": "代码检查缺省分数"},
            {"key": "allow_student_change_password", "value": "true", "description": "是否允许学生修改自己密码"}
        ]
        
        for setting in settings:
            existing = db.query(SystemSetting).filter(SystemSetting.key == setting["key"]).first()
            if not existing:
                db.add(SystemSetting(**setting))
                print(f"已创建系统设置: {setting['key']} = {setting['value']}")
        
        # 提交事务
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("数据库初始化完成!") 