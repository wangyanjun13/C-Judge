import redis
import json
import os
from datetime import datetime
from typing import Optional, Any
from config.settings import settings

class DateTimeEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Redis连接配置
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# 创建Redis连接池 - 4核8G服务器高并发优化配置
redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=100,       # 增加连接池大小以支持100+并发
    retry_on_timeout=True,
    socket_keepalive=True,
    socket_keepalive_options={},
    health_check_interval=30,  # 减少健康检查间隔，提高响应速度
    socket_connect_timeout=5,  # 增加连接超时时间
    socket_timeout=5,          # 增加操作超时时间
    decode_responses=True,
    retry_on_error=[redis.ConnectionError, redis.TimeoutError]
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool, decode_responses=True)

class RedisCache:
    """Redis缓存工具类"""
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, cls=DateTimeEncoder)
            return redis_client.set(key, value, ex=expire)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = redis_client.get(key)
            if value is None:
                return None
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @staticmethod
    def delete(key: str) -> bool:
        """删除缓存"""
        try:
            return redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """检查键是否存在"""
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    @staticmethod
    def set_user_session(user_id: int, session_data: dict, expire: int = 86400) -> bool:
        """设置用户会话"""
        key = f"user_session:{user_id}"
        return RedisCache.set(key, session_data, expire)
    
    @staticmethod
    def get_user_session(user_id: int) -> Optional[dict]:
        """获取用户会话"""
        key = f"user_session:{user_id}"
        return RedisCache.get(key)
    
    @staticmethod
    def delete_user_session(user_id: int) -> bool:
        """删除用户会话"""
        key = f"user_session:{user_id}"
        return RedisCache.delete(key)
    
    @staticmethod
    def set_online_users(users: list, expire: int = 60) -> bool:
        """缓存在线用户列表"""
        key = "online_users"
        return RedisCache.set(key, users, expire)
    
    @staticmethod
    def get_online_users() -> Optional[list]:
        """获取在线用户列表"""
        key = "online_users"
        return RedisCache.get(key)
    
    @staticmethod
    def increment_login_attempts(username: str, expire: int = 300) -> int:
        """增加登录尝试次数"""
        key = f"login_attempts:{username}"
        try:
            attempts = redis_client.incr(key)
            if attempts == 1:
                redis_client.expire(key, expire)
            return attempts
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    @staticmethod
    def clear_login_attempts(username: str) -> bool:
        """清除登录尝试次数"""
        key = f"login_attempts:{username}"
        return RedisCache.delete(key)
