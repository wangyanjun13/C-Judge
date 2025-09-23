#!/usr/bin/env python3
"""
C-Judge 系统压力测试脚本
模拟100+用户同时登录操作
"""

import asyncio
import aiohttp
import time
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import statistics

class LoadTester:
    def __init__(self, base_url: str = "http://localhost:8000", concurrent_users: int = 100):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # 从文件加载真实学生数据
        self.test_users = self.load_student_data()

    def load_student_data(self) -> List[Dict[str, str]]:
        """从students_list.txt文件加载学生数据"""
        students = []
        try:
            with open('students_list.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 3:
                            students.append({
                                "username": parts[0],  # 学号
                                "password": parts[1],  # 密码
                                "name": parts[2],      # 真实姓名
                                "role": "student"
                            })
            print(f"✅ 成功加载 {len(students)} 个学生数据")
        except FileNotFoundError:
            print("❌ 未找到 students_list.txt 文件，使用默认测试用户")
            students = [
                {"username": "admin", "password": "admin", "role": "admin"},
                {"username": "teacher", "password": "teacher", "role": "teacher"},
                {"username": "student", "password": "student", "role": "student"},
            ]
        except Exception as e:
            print(f"❌ 加载学生数据时出错: {e}")
            students = [{"username": "student", "password": "student", "role": "student"}]
        
        return students

    async def login_user(self, session: aiohttp.ClientSession, user_data: Dict[str, str], user_id: int) -> Dict[str, Any]:
        """单个用户登录测试"""
        login_start = time.time()
        
        try:
            # 准备登录数据
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            # 发送登录请求
            async with session.post(
                f"{self.base_url}/api/auth/login",
                data=login_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - login_start
                
                if response.status == 200:
                    result_data = await response.json()
                    return {
                        "user_id": user_id,
                        "username": user_data["username"],
                        "status": "success",
                        "response_time": response_time,
                        "status_code": response.status,
                        "has_token": "access_token" in result_data,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "user_id": user_id,
                        "username": user_data["username"],
                        "status": "failed",
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": error_text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except asyncio.TimeoutError:
            return {
                "user_id": user_id,
                "username": user_data["username"],
                "status": "timeout",
                "response_time": 30.0,
                "status_code": 0,
                "error": "Request timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "user_id": user_id,
                "username": user_data["username"],
                "status": "error",
                "response_time": time.time() - login_start,
                "status_code": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def run_concurrent_login_test(self):
        """运行并发登录测试"""
        print(f"🚀 开始压力测试: {self.concurrent_users} 个用户同时登录")
        print(f"📡 目标服务器: {self.base_url}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        self.start_time = time.time()
        
        # 创建HTTP会话
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=200)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建并发任务
            tasks = []
            for i, user_data in enumerate(self.test_users[:self.concurrent_users]):
                task = self.login_user(session, user_data, i + 1)
                tasks.append(task)
            
            # 等待所有任务完成
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.end_time = time.time()
        
        # 处理异常结果
        processed_results = []
        for result in self.results:
            if isinstance(result, Exception):
                processed_results.append({
                    "user_id": 0,
                    "username": "unknown",
                    "status": "exception",
                    "response_time": 0,
                    "status_code": 0,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        self.results = processed_results

    def analyze_results(self):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return
        
        total_time = self.end_time - self.start_time
        successful_logins = [r for r in self.results if r["status"] == "success"]
        failed_logins = [r for r in self.results if r["status"] != "success"]
        
        response_times = [r["response_time"] for r in successful_logins if r["response_time"] > 0]
        
        print("\n" + "=" * 60)
        print("📊 压力测试结果分析")
        print("=" * 60)
        
        print(f"⏱️  总测试时间: {total_time:.2f} 秒")
        print(f"👥 总用户数: {len(self.results)}")
        print(f"✅ 成功登录: {len(successful_logins)} ({len(successful_logins)/len(self.results)*100:.1f}%)")
        print(f"❌ 失败登录: {len(failed_logins)} ({len(failed_logins)/len(self.results)*100:.1f}%)")
        
        if response_times:
            print(f"\n📈 响应时间统计:")
            print(f"   平均响应时间: {statistics.mean(response_times):.3f} 秒")
            print(f"   中位数响应时间: {statistics.median(response_times):.3f} 秒")
            print(f"   最小响应时间: {min(response_times):.3f} 秒")
            print(f"   最大响应时间: {max(response_times):.3f} 秒")
            print(f"   95%分位数: {sorted(response_times)[int(len(response_times)*0.95)]:.3f} 秒")
        
        print(f"\n🚀 系统吞吐量:")
        print(f"   每秒请求数 (RPS): {len(self.results)/total_time:.2f}")
        print(f"   每秒成功登录数: {len(successful_logins)/total_time:.2f}")
        
        # 错误分析
        if failed_logins:
            print(f"\n❌ 失败原因分析:")
            error_counts = {}
            for result in failed_logins:
                error_type = result.get("error", "未知错误")
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count} 次")

    def save_results(self, filename: str = None):
        """保存测试结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        report = {
            "test_info": {
                "concurrent_users": self.concurrent_users,
                "base_url": self.base_url,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration": self.end_time - self.start_time
            },
            "summary": {
                "total_users": len(self.results),
                "successful_logins": len([r for r in self.results if r["status"] == "success"]),
                "failed_logins": len([r for r in self.results if r["status"] != "success"])
            },
            "detailed_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到: {filename}")

async def main():
    """主函数"""
    print("🎯 C-Judge 系统压力测试工具")
    print("=" * 60)
    
    # 创建压力测试器 - 使用200个真实学生数据
    tester = LoadTester(concurrent_users=200)
    
    try:
        # 运行测试
        await tester.run_concurrent_login_test()
        
        # 分析结果
        tester.analyze_results()
        
        # 保存结果
        tester.save_results()
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
