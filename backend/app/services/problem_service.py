import os
import shutil
import logging
from typing import List, Optional
from app.schemas.problem import ProblemCategory, ProblemInfo

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 题库根目录 - 只使用项目根目录下的题库路径
PROBLEMS_ROOT = "/app_root/题库"  # Docker挂载的项目根目录下的题库

logger.info(f"设置题库根目录为: {PROBLEMS_ROOT}")
logger.info(f"题库目录是否存在: {os.path.exists(PROBLEMS_ROOT)}")
logger.info(f"当前工作目录: {os.getcwd()}")

class ProblemService:
    @staticmethod
    def get_problem_categories() -> List[ProblemCategory]:
        """获取所有题库分类"""
        categories = []
        
        # 确保题库目录存在，但不创建
        if not os.path.exists(PROBLEMS_ROOT):
            logger.error(f"题库目录不存在: {PROBLEMS_ROOT}")
            logger.info(f"当前工作目录: {os.getcwd()}")
            # 不尝试创建目录，直接返回空列表
            return categories
        
        logger.info(f"题库目录存在，开始扫描子目录")
        
        # 遍历题库根目录下的所有子目录
        for base_dir in os.listdir(PROBLEMS_ROOT):
            base_path = os.path.join(PROBLEMS_ROOT, base_dir)
            if os.path.isdir(base_path):
                logger.info(f"扫描基础题库: {base_dir}")
                # 遍历基础题库下的分类目录
                for category_dir in os.listdir(base_path):
                    category_path = os.path.join(base_path, category_dir)
                    if os.path.isdir(category_path):
                        # 提取分类名称（如"1.顺序结构"中的"顺序结构"）
                        category_name = category_dir
                        if "." in category_dir:
                            parts = category_dir.split(".", 1)
                            if len(parts) > 1:
                                category_name = parts[1]
                        
                        logger.info(f"找到分类: {category_name}, 路径: {os.path.join(base_dir, category_dir)}")
                        categories.append(ProblemCategory(
                            name=category_name,
                            path=os.path.join(base_dir, category_dir)
                        ))
        
        logger.info(f"共找到 {len(categories)} 个题库分类")
        return categories
    
    @staticmethod
    def get_problems_by_category(category_path: str) -> List[ProblemInfo]:
        """获取指定分类下的所有试题"""
        problems = []
        full_path = os.path.join(PROBLEMS_ROOT, category_path)
        
        logger.info(f"获取分类 {category_path} 下的试题，完整路径: {full_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"题库分类不存在: {full_path}")
            return problems
        
        # 遍历分类目录下的所有试题文件夹
        for problem_dir in os.listdir(full_path):
            problem_path = os.path.join(full_path, problem_dir)
            if os.path.isdir(problem_path):
                # 读取Question.INF文件
                inf_path = os.path.join(problem_path, "Question.INF")
                if os.path.exists(inf_path):
                    logger.info(f"找到试题: {problem_dir}, 正在解析 Question.INF")
                    problem_info = ProblemService.parse_question_inf(inf_path, problem_dir, category_path)
                    if problem_info:
                        problems.append(problem_info)
        
        logger.info(f"分类 {category_path} 下共找到 {len(problems)} 个试题")
        return problems
    
    @staticmethod
    def delete_problem(problem_path: str) -> str:
        """删除试题"""
        full_path = os.path.join(PROBLEMS_ROOT, problem_path)
        
        logger.info(f"尝试删除试题: {problem_path}, 完整路径: {full_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"试题不存在: {full_path}")
            raise FileNotFoundError(f"试题不存在: {problem_path}")
        
        # 删除试题文件夹
        shutil.rmtree(full_path)
        logger.info(f"试题 {problem_path} 已成功删除")
        return f"试题 {problem_path} 已成功删除"
    
    @staticmethod
    def parse_question_inf(inf_path: str, problem_name: str, category_path: str) -> Optional[ProblemInfo]:
        """解析Question.INF文件，提取试题信息"""
        chinese_name = ""
        time_limit = ""
        memory_limit = ""
        
        # 尝试不同的编码格式
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
        
        for encoding in encodings:
            try:
                with open(inf_path, "r", encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("试题中文名称="):
                            chinese_name = line.split("=", 1)[1].strip('"')
                        elif line.startswith("时间限制="):
                            time_limit = line.split("=", 1)[1].split("//")[0].strip()
                        elif line.startswith("内存限制="):
                            memory_limit = line.split("=", 1)[1].split("//")[0].strip()
                
                logger.info(f"成功使用 {encoding} 编码解析试题: {problem_name}, 中文名称: {chinese_name}")
                return ProblemInfo(
                    name=problem_name,
                    chinese_name=chinese_name,
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                    data_path=os.path.join(category_path, problem_name),
                    category=category_path.split("/")[-1] if "/" in category_path else category_path
                )
            except UnicodeDecodeError:
                logger.debug(f"使用 {encoding} 编码解析失败，尝试下一种编码")
                continue
            except Exception as e:
                logger.error(f"解析试题信息失败: {str(e)}")
                return None
        
        logger.error(f"所有编码尝试均失败，无法解析文件: {inf_path}")
        return None 