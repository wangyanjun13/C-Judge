import os
import requests
import hashlib
import subprocess
import tempfile
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.models import Submission, Problem
from config.settings import settings

class JudgeService:
    """评测服务"""
    
    @staticmethod
    def run_code_check(code: str, language: str) -> Dict[str, Any]:
        """
        运行代码检查，计算代码检查得分(20分)
        简单实现：检查代码是否能编译通过
        """
        if language == "c":
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as temp:
                temp_file_name = temp.name
                temp.write(code.encode('utf-8'))
            
            try:
                # 使用gcc尝试编译
                result = subprocess.run(
                    ['gcc', '-Wall', '-o', f"{temp_file_name}.out", temp_file_name], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                # 删除临时文件
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
                if os.path.exists(f"{temp_file_name}.out"):
                    os.remove(f"{temp_file_name}.out")
                
                # 检查编译结果
                if result.returncode == 0:
                    # 编译成功，给予满分
                    return {
                        "passed": True,
                        "score": 20,
                        "message": "代码编译成功"
                    }
                else:
                    # 编译失败
                    return {
                        "passed": False,
                        "score": 0,
                        "message": f"编译错误: {result.stderr}"
                    }
            
            except Exception as e:
                # 删除临时文件
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
                if os.path.exists(f"{temp_file_name}.out"):
                    os.remove(f"{temp_file_name}.out")
                
                return {
                    "passed": False,
                    "score": 0,
                    "message": f"代码检查错误: {str(e)}"
                }
        else:
            # 其他语言暂不支持，给予默认分数
            return {
                "passed": True,
                "score": 20,
                "message": f"语言 {language} 暂不支持代码检查，默认给予满分"
            }
    
    @staticmethod
    def run_judge(problem: Problem, code: str, language: str) -> Dict[str, Any]:
        """
        调用评测服务，运行测试用例(80分)
        """
        # 检查测试数据路径是否存在
        test_case_dir = os.path.join("/root_project", problem.data_path) if problem.data_path else ""
        if not problem.data_path or not os.path.exists(test_case_dir):
            # 测试数据不存在，返回默认满分
            return {
                "passed": True,
                "score": 80,
                "message": "无测试用例，默认给予满分",
                "details": []
            }
        
        # 确保时间和内存限制有效
        time_limit = problem.time_limit if problem.time_limit else 1000  # 默认1秒
        memory_limit = problem.memory_limit if problem.memory_limit else 134217728  # 默认128MB
        
        # 构造请求头
        headers = {
            "Content-Type": "application/json",
            "X-Judge-Server-Token": hashlib.sha256(settings.JUDGE_SERVER_TOKEN.encode()).hexdigest()
        }
        
        # 构造请求体
        data = {
            "src": code,
            "language_config": {
                "compile": {
                    "src_name": "main.c",
                    "exe_name": "main",
                    "max_cpu_time": 3000,  # 编译时间限制，可以稍微大一点
                    "max_real_time": 5000,
                    "max_memory": 134217728,  # 编译内存限制，可以稍微大一点
                    "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}"
                },
                "run": {
                    "command": "{exe_path}",
                    "seccomp_rule": "c_cpp",
                    "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
                }
            },
            "max_cpu_time": time_limit,
            "max_memory": memory_limit,
            "test_case_id": problem.data_path,
            "output": False
        }
        
        try:
            # 发送请求到评测服务
            response = requests.post(
                f"{settings.JUDGE_SERVER_URL}/judge",
                headers=headers,
                json=data,
                timeout=30
            )
            
            # 检查响应
            response.raise_for_status()
            result = response.json()
            
            if "err" in result and result["err"]:
                # 尝试解析错误信息
                error_msg = result.get("data", "未知错误")
                
                # 如果是测试用例不存在的错误，给予默认满分
                if "Test case not found" in str(error_msg) or "No such file or directory" in str(error_msg):
                    return {
                        "passed": True,
                        "score": 80,
                        "message": "测试用例不存在或格式错误，默认给予满分",
                        "details": []
                    }
                
                # 其他评测错误
                return {
                    "passed": False,
                    "score": 0,
                    "message": f"评测错误: {error_msg}",
                    "details": result
                }
            else:
                # 计算得分
                return JudgeService._calculate_score(result, problem.runtime_score)
        
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            
            # 如果是测试用例相关错误，给予默认满分
            if "Test case not found" in error_msg or "No such file or directory" in error_msg:
                return {
                    "passed": True,
                    "score": 80,
                    "message": "测试用例不存在或格式错误，默认给予满分",
                    "details": []
                }
            
            return {
                "passed": False,
                "score": 0,
                "message": f"评测服务请求失败: {error_msg}",
                "details": {"error": error_msg}
            }
        except Exception as e:
            error_msg = str(e)
            
            # 如果是测试用例相关错误，给予默认满分
            if "Test case not found" in error_msg or "No such file or directory" in error_msg:
                return {
                    "passed": True,
                    "score": 80,
                    "message": "测试用例不存在或格式错误，默认给予满分",
                    "details": []
                }
            
            return {
                "passed": False,
                "score": 0,
                "message": f"评测过程出错: {error_msg}",
                "details": {"error": error_msg}
            }
    
    @staticmethod
    def _calculate_score(judge_result: List[Dict], total_score: int = 80) -> Dict[str, Any]:
        """
        计算运行评测得分
        """
        if not judge_result or not isinstance(judge_result, list):
            return {
                "passed": False,
                "score": 0,
                "message": "无效的评测结果",
                "details": judge_result
            }
        
        # 计算通过的测试点数量
        total_test_cases = len(judge_result)
        passed_test_cases = sum(1 for case in judge_result if case.get("result") == 0)
        
        # 如果全部通过
        if passed_test_cases == total_test_cases:
            return {
                "passed": True,
                "score": total_score,
                "message": f"通过所有测试点 ({passed_test_cases}/{total_test_cases})",
                "details": judge_result
            }
        
        # 部分通过
        if passed_test_cases > 0:
            score = int(total_score * passed_test_cases / total_test_cases)
            return {
                "passed": False,
                "score": score,
                "message": f"部分通过测试点 ({passed_test_cases}/{total_test_cases})",
                "details": judge_result
            }
        
        # 全部失败
        return {
            "passed": False,
            "score": 0,
            "message": "未通过任何测试点",
            "details": judge_result
        }
    
    @staticmethod
    def submit(db: Session, user_id: int, problem_id: int, exercise_id: Optional[int], 
               code: str, language: str = "c") -> Submission:
        """
        提交代码并评测
        """
        # 获取问题信息
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError(f"问题不存在: ID {problem_id}")
        
        # 创建提交记录
        submission = Submission(
            user_id=user_id,
            problem_id=problem_id,
            exercise_id=exercise_id,
            code=code,
            language=language,
            status="Pending"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        try:
            # 进行代码检查
            code_check_result = JudgeService.run_code_check(code, language)
            code_check_score = code_check_result.get("score", 0)
            
            # 如果代码检查未通过，则不进行运行测试
            if not code_check_result.get("passed", False):
                submission.status = "Compilation Error"
                submission.code_check_score = code_check_score
                submission.runtime_score = 0
                submission.total_score = code_check_score
                submission.result = {
                    "code_check": code_check_result,
                    "runtime": {"passed": False, "score": 0, "message": "编译失败，未运行测试"}
                }
                db.commit()
                return submission
            
            # 进行运行测试
            runtime_result = JudgeService.run_judge(problem, code, language)
            runtime_score = runtime_result.get("score", 0)
            
            # 更新提交记录
            submission.code_check_score = code_check_score
            submission.runtime_score = runtime_score
            submission.total_score = code_check_score + runtime_score
            
            # 设置状态
            if runtime_result.get("passed", False):
                submission.status = "Accepted"
            else:
                submission.status = "Wrong Answer"
            
            # 保存结果详情
            submission.result = {
                "code_check": code_check_result,
                "runtime": runtime_result
            }
            
            db.commit()
            return submission
            
        except Exception as e:
            submission.status = "System Error"
            submission.code_check_score = 0
            submission.runtime_score = 0
            submission.total_score = 0
            submission.result = {"error": str(e)}
            db.commit()
            
            # 记录错误但不抛出，以便让API能正确返回
            import traceback
            traceback.print_exc()
            
            return submission 