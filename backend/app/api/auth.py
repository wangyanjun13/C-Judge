from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models import User, get_db, OperationLog
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_active_user
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新用户在线状态
    user.is_online = True
    db.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=user.id,
        operation="登录",
        target="系统"
    )
    db.add(log)
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # 将用户对象转换为字典
    user_dict = {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "is_online": user.is_online,
        "register_time": user.register_time.isoformat() if user.register_time else None
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册（仅用于开发阶段，生产环境应由管理员创建用户）"""
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被使用")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        password=hashed_password,
        real_name=user_data.real_name,
        role=user_data.role
        # 数据库中没有 class_id 字段，暂时注释掉
        # class_id=user_data.class_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 记录操作日志
    log = OperationLog(
        user_id=db_user.id,
        operation="注册",
        target="系统"
    )
    db.add(log)
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    
    # 将用户对象转换为字典
    user_dict = {
        "id": db_user.id,
        "username": db_user.username,
        "real_name": db_user.real_name,
        "role": db_user.role,
        "is_online": db_user.is_online,
        "register_time": db_user.register_time.isoformat() if db_user.register_time else None
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 更新密码
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="修改密码",
        target="系统"
    )
    db.add(log)
    db.commit()
    
    return {"message": "密码修改成功"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """用户登出"""
    # 更新用户在线状态
    current_user.is_online = False
    db.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        operation="登出",
        target="系统"
    )
    db.add(log)
    db.commit()
    
    return {"message": "登出成功"}

@router.post("/logout-simple")
async def logout_simple():
    """简化版登出 - 不需要身份验证"""
    return {"message": "登出成功"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user 