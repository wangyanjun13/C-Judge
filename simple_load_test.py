#!/usr/bin/env python3
"""
C-Judge 系统简单压力测试脚本
使用标准库进行压力测试，无需额外依赖
"""

import requests
import threading
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class SimpleLoadTester:
    def __init__(self, base_url="http://localhost:8000", max_workers=100):
        self.base_url = base_url
        self.max_workers = max_workers
        self.results = []
        self.lock = threading.Lock()
        
        # 测试用户数据
        self.test_users = [
            {"username": "admin", "password": "admin"},
            {"username": "teacher", "password": "teacher"},
            {"username": "student", "password": "student"},
        ]
        
        # 生成更多测试用户
        for i in range(1, 98):
            self.test_users.append({
                "username": f"testuser{i:03d}",
                "password": "password123"
            })

    def login_user(self, user_data, user_id):
        """单个用户登录测试"""
        start_time = time.time()
        
        try:
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                data=login_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            result = {
                "user_id": user_id,
                "username": user_data["username"],
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["status"] = "success"
                    result["has_token"] = "access_token" in data
                except:
                    result["status"] = "success_no_json"
            elif response.status_code == 401:
                result["status"] = "unauthorized"
                result["error"] = "用户名或密码错误"
            elif response.status_code == 429:
                result["status"] = "rate_limited"
                result["error"] = "登录尝试次数过多"
            else:
                result["status"] = "failed"
                result["error"] = f"HTTP {response.status_code}"
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                "user_id": user_id,
                "username": user_data["username"],
                "status": "timeout",
                "response_time": 30.0,
                "status_code": 0,
                "error": "请求超时",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "user_id": user_id,
                "username": user_data["username"],
                "status": "error",
                "response_time": time.time() - start_time,
                "status_code": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_load_test(self, concurrent_users=100):
        """运行压力测试"""
        print(f"🚀 开始压力测试: {concurrent_users} 个用户同时登录")
        print(f"📡 目标服务器: {self.base_url}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        start_time = time.time()
        
        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有任务
            futures = []
            for i, user_data in enumerate(self.test_users[:concurrent_users]):
                future = executor.submit(self.login_user, user_data, i + 1)
                futures.append(future)
            
            # 收集结果
            self.results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    print(f"❌ 任务执行异常: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析结果
        self.analyze_results(total_time)

    def analyze_results(self, total_time):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return
        
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
            if len(response_times) > 20:
                print(f"   95%分位数: {sorted(response_times)[int(len(response_times)*0.95)]:.3f} 秒")
        
        print(f"\n🚀 系统吞吐量:")
        print(f"   每秒请求数 (RPS): {len(self.results)/total_time:.2f}")
        print(f"   每秒成功登录数: {len(successful_logins)/total_time:.2f}")
        
        # 错误分析
        if failed_logins:
            print(f"\n❌ 失败原因分析:")
            error_counts = {}
            for result in failed_logins:
                error_type = result.get("error", result.get("status", "未知错误"))
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count} 次")
        
        # 性能评估
        print(f"\n🎯 性能评估:")
        if len(successful_logins) / len(self.results) >= 0.95:
            print("   ✅ 系统稳定性: 优秀 (成功率 ≥ 95%)")
        elif len(successful_logins) / len(self.results) >= 0.90:
            print("   ⚠️  系统稳定性: 良好 (成功率 ≥ 90%)")
        else:
            print("   ❌ 系统稳定性: 需要优化 (成功率 < 90%)")
        
        if response_times and statistics.mean(response_times) <= 1.0:
            print("   ✅ 响应速度: 优秀 (平均响应时间 ≤ 1秒)")
        elif response_times and statistics.mean(response_times) <= 3.0:
            print("   ⚠️  响应速度: 良好 (平均响应时间 ≤ 3秒)")
        else:
            print("   ❌ 响应速度: 需要优化 (平均响应时间 > 3秒)")

    def save_results(self, filename=None):
        """保存测试结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        report = {
            "test_info": {
                "base_url": self.base_url,
                "max_workers": self.max_workers,
                "timestamp": datetime.now().isoformat()
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

def main():
    """主函数"""
    print("🎯 C-Judge 系统简单压力测试工具")
    print("=" * 60)
    
    # 创建压力测试器
    tester = SimpleLoadTester()
    
    try:
        # 运行测试
        tester.run_load_test(concurrent_users=100)
        
        # 保存结果
        tester.save_results()
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
