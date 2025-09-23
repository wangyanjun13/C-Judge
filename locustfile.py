"""
C-Judge 系统压力测试 - Locust版本
使用Locust进行专业的压力测试
"""

from locust import HttpUser, task, between
import random
import json

class CJudgeUser(HttpUser):
    """C-Judge系统用户行为模拟"""
    
    wait_time = between(1, 3)  # 用户操作间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化操作"""
        self.username = None
        self.password = None
        self.token = None
        
        # 随机选择一个测试用户
        test_users = [
            {"username": "admin", "password": "admin"},
            {"username": "teacher", "password": "teacher"},
            {"username": "student", "password": "student"},
        ]
        
        # 添加更多测试用户
        for i in range(1, 50):
            test_users.append({
                "username": f"testuser{i:03d}",
                "password": "password123"
            })
        
        user = random.choice(test_users)
        self.username = user["username"]
        self.password = user["password"]
    
    @task(10)
    def login(self):
        """登录操作 - 权重最高"""
        login_data = {
            "username": self.username,
            "password": self.password
        }
        
        with self.client.post(
            "/api/auth/login",
            data=login_data,
            catch_response=True,
            name="用户登录"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result:
                    self.token = result["access_token"]
                    response.success()
                else:
                    response.failure("登录响应中缺少access_token")
            elif response.status_code == 401:
                response.failure("用户名或密码错误")
            elif response.status_code == 429:
                response.failure("登录尝试次数过多")
            else:
                response.failure(f"登录失败，状态码: {response.status_code}")
    
    @task(3)
    def get_user_info(self):
        """获取用户信息 - 需要登录"""
        if not self.token:
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.get(
            "/api/users/me",
            headers=headers,
            catch_response=True,
            name="获取用户信息"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("未授权访问")
            else:
                response.failure(f"获取用户信息失败，状态码: {response.status_code}")
    
    @task(2)
    def get_problems(self):
        """获取题目列表 - 需要登录"""
        if not self.token:
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.get(
            "/api/problems/",
            headers=headers,
            catch_response=True,
            name="获取题目列表"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("未授权访问")
            else:
                response.failure(f"获取题目列表失败，状态码: {response.status_code}")
    
    @task(1)
    def get_submissions(self):
        """获取提交记录 - 需要登录"""
        if not self.token:
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.get(
            "/api/submissions/",
            headers=headers,
            catch_response=True,
            name="获取提交记录"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("未授权访问")
            else:
                response.failure(f"获取提交记录失败，状态码: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """健康检查 - 不需要登录"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="健康检查"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"健康检查失败，状态码: {response.status_code}")

class LoginOnlyUser(HttpUser):
    """仅登录测试用户 - 专门测试登录性能"""
    
    wait_time = between(0.1, 0.5)  # 更短的等待时间
    
    def on_start(self):
        """初始化测试用户"""
        self.user_id = random.randint(1, 1000)
        self.username = f"loadtest_user_{self.user_id}"
        self.password = "password123"
    
    @task
    def login_only(self):
        """仅执行登录操作"""
        login_data = {
            "username": self.username,
            "password": self.password
        }
        
        with self.client.post(
            "/api/auth/login",
            data=login_data,
            catch_response=True,
            name="压力测试登录"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result:
                    response.success()
                else:
                    response.failure("登录响应中缺少access_token")
            elif response.status_code == 401:
                response.failure("用户名或密码错误")
            elif response.status_code == 429:
                response.failure("登录尝试次数过多")
            else:
                response.failure(f"登录失败，状态码: {response.status_code}")
