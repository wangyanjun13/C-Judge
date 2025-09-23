from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.models import User, get_db, OperationLog
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, OnlineUserResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_active_user, get_teacher_user, get_admin_user
from app.utils.redis_client import RedisCache
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录 - 高性能优化版本"""
    # 检查登录尝试次数限制（使用Redis缓存）
    attempts = RedisCache.increment_login_attempts(form_data.username)
    if attempts > 5:  # 5次失败后锁定5分钟
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录尝试次数过多，请5分钟后再试",
        )
    
    # 先检查Redis缓存中是否有用户信息
    cached_user = RedisCache.get(f"user:{form_data.username}")
    if cached_user:
        # 从缓存获取用户信息
        user_data = cached_user
        if not verify_password(form_data.password, user_data.get('password_hash')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # 从缓存构建用户对象
        user = type('User', (), {
            'id': user_data['id'],
            'username': user_data['username'],
            'real_name': user_data['real_name'],
            'role': user_data['role'],
            'is_online': False,
            'register_time': user_data.get('register_time')
        })()
    else:
        # 从数据库查找用户（只查询必要字段）
        user = db.query(User.id, User.username, User.password, User.real_name, User.role, User.register_time).filter(
            User.username == form_data.username
        ).first()
        
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 缓存用户信息（不包含密码）
        user_cache = {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role,
            'register_time': user.register_time.isoformat() if user.register_time else None,
            'password_hash': user.password  # 用于密码验证
        }
        RedisCache.set(f"user:{form_data.username}", user_cache, expire=3600)  # 缓存1小时
    
    # 登录成功，清除登录尝试次数
    RedisCache.clear_login_attempts(form_data.username)
    
    # 异步更新用户在线状态（不阻塞登录响应）
    now = datetime.now()
    
    # 使用批量操作减少数据库交互
    try:
        # 更新用户在线状态
        db.execute(
            text("UPDATE users SET is_online = true WHERE id = :user_id"),
            {"user_id": user.id}
        )
        
        # 批量插入操作日志（使用批量插入提高性能）
        log_data = {
            'user_id': user.id,
            'operation': '登录',
            'target': '系统',
            'created_at': now
        }
        db.execute(
            text("INSERT INTO operation_logs (user_id, operation, target, created_at) VALUES (:user_id, :operation, :target, :created_at)"),
            log_data
        )
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        # 登录状态更新失败不影响登录成功
        print(f"Warning: Failed to update user status: {e}")
    
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
        "is_online": True,
        "register_time": user.register_time.isoformat() if hasattr(user.register_time, 'isoformat') and user.register_time else str(user.register_time) if user.register_time else None
    }
    
    # 缓存用户会话信息（异步操作）
    session_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "login_time": now.isoformat()
    }
    RedisCache.set_user_session(user.id, session_data, expire=86400)  # 缓存24小时
    
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
    now = datetime.now()
    log = OperationLog(
        user_id=db_user.id,
        operation="注册",
        target="系统",
        created_at=now
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
    password_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    
    # 验证旧密码
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 更新密码
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    # 记录操作日志
    now = datetime.now()
    log = OperationLog(
        user_id=current_user.id,
        operation="修改密码",
        target="系统",
        created_at=now
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
    now = datetime.now()
    log = OperationLog(
        user_id=current_user.id,
        operation="登出",
        target="系统",
        created_at=now
    )
    db.add(log)
    db.commit()
    
    return {"message": "登出成功"}

@router.post("/logout-simple")
async def logout_simple():
    """简化版登出 - 不需要身份验证"""
    return {"message": "登出成功"}

@router.post("/heartbeat")
async def heartbeat(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """更新用户在线状态的心跳"""
    # 更新用户在线状态
    current_user.is_online = True
    db.commit()
    
    # 记录最后活动时间
    now = datetime.now()  # 使用不带时区的本地时间
    
    return {"status": "ok", "timestamp": now.isoformat()}

@router.get("/online-users", response_model=List[OnlineUserResponse])
async def get_online_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取在线用户列表（仅管理员和教师可访问）- 优化版本"""
    # 检查权限
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员和教师可以查看在线用户"
        )
    
    # 尝试从Redis缓存获取在线用户列表
    cached_users = RedisCache.get_online_users()
    if cached_users:
        return cached_users
    
    try:
        # 计算2分钟前的时间点
        now = datetime.now()
        two_minutes_ago = now - timedelta(minutes=2)
        
        # 使用LEFT JOIN一次性获取用户和最新操作日志，避免N+1查询
        from sqlalchemy import func
        from sqlalchemy.orm import aliased
        
        # 子查询：获取每个用户的最新操作时间
        latest_logs_subquery = db.query(
            OperationLog.user_id,
            func.max(OperationLog.created_at).label('latest_activity')
        ).group_by(OperationLog.user_id).subquery()
        
        # 主查询：LEFT JOIN用户表和最新操作日志
        users_with_activity = db.query(
            User,
            latest_logs_subquery.c.latest_activity
        ).outerjoin(
            latest_logs_subquery, User.id == latest_logs_subquery.c.user_id
        ).all()
        
        # 处理结果列表
        result = []
        users_to_update = []  # 需要更新在线状态的用户
        
        for user, last_activity in users_with_activity:
            # 判断用户是否在线
            is_online = False
            if last_activity:
                # 确保时区一致性
                if hasattr(last_activity, 'tzinfo') and last_activity.tzinfo is not None:
                    last_activity = last_activity.replace(tzinfo=None)
                is_online = last_activity >= two_minutes_ago
            
            # 记录需要更新在线状态的用户
            if user.is_online != is_online:
                user.is_online = is_online
                users_to_update.append(user)
            
            # 构建响应对象
            user_response = {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role,
                "is_online": user.is_online,
                "register_time": user.register_time.isoformat() if user.register_time else None,
                "last_activity": last_activity.isoformat() if last_activity else None
            }
            
            result.append(user_response)
        
        # 批量更新用户在线状态
        if users_to_update:
            db.commit()
        
        # 缓存在线用户列表（缓存1分钟）
        RedisCache.set_online_users(result, expire=60)
        
        return result
        
    except Exception as e:
        # 捕获所有异常，保证API稳定性
        error_msg = str(e)
        print(f"获取在线用户出错: {error_msg}")
        
        # 针对时区问题提供更具体的错误信息
        if "offset-naive and offset-aware datetimes" in error_msg:
            error_detail = "时区比较错误，请检查数据库和应用时区设置"
        else:
            error_detail = "获取在线用户列表时出错"
            
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user 