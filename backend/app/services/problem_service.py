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

logger.info(f"题库根目录: {PROBLEMS_ROOT}")

class ProblemService:
    @staticmethod
    def get_problem_categories() -> List[ProblemCategory]:
        """获取所有题库分类"""
        categories = []
        
        # 确保题库目录存在，但不创建
        if not os.path.exists(PROBLEMS_ROOT):
            logger.error(f"题库目录不存在: {PROBLEMS_ROOT}")
            return categories
        
        # 递归查找所有包含试题的目录
        ProblemService._find_categories(PROBLEMS_ROOT, "", categories)
        
        return categories
    
    @staticmethod
    def _find_categories(current_path: str, relative_path: str, categories: List[ProblemCategory]) -> None:
        """递归查找所有题库分类"""
        # 检查当前目录是否包含试题
        has_problems = False
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                inf_path = os.path.join(item_path, "Question.INF")
                if os.path.exists(inf_path):
                    has_problems = True
                    break
        
        # 如果当前目录包含试题，将其添加为一个分类
        if has_problems:
            # 处理分类名称，过滤掉"题库X.X"这样的最高层目录
            path_parts = relative_path.split(os.sep)
            if path_parts and path_parts[0].startswith("题库"):
                # 如果第一部分是"题库X.X"，则从第二部分开始显示
                if len(path_parts) > 1:
                    category_name = os.sep.join(path_parts[1:])
                else:
                    category_name = relative_path
            else:
                category_name = relative_path
            
            logger.info(f"添加题库分类: {category_name}, 路径: {relative_path}")
            categories.append(ProblemCategory(
                name=category_name,
                path=relative_path
            ))
        else:
            # 如果当前目录不包含试题，继续递归查找子目录
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    new_relative_path = os.path.join(relative_path, item) if relative_path else item
                    ProblemService._find_categories(item_path, new_relative_path, categories)
    
    @staticmethod
    def get_problems_by_category(category_path: str) -> List[ProblemInfo]:
        """获取指定分类下的所有试题"""
        problems = []
        full_path = os.path.join(PROBLEMS_ROOT, category_path)
        
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
                    problem_info = ProblemService.parse_question_inf(inf_path, problem_dir, category_path)
                    if problem_info:
                        problems.append(problem_info)
        
        return problems
    
    @staticmethod
    def delete_problem(problem_path: str) -> str:
        """删除试题"""
        full_path = os.path.join(PROBLEMS_ROOT, problem_path)
        
        logger.info(f"删除试题: {problem_path}")
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.error(f"试题不存在: {full_path}")
            raise FileNotFoundError(f"试题不存在: {problem_path}")
        
        # 删除试题文件夹
        shutil.rmtree(full_path)
        return f"试题 {problem_path} 已成功删除"
    
    @staticmethod
    def parse_question_inf(inf_path: str, problem_name: str, category_path: str) -> Optional[ProblemInfo]:
        """解析Question.INF文件，提取试题信息"""
        chinese_name = ""
        time_limit = ""
        memory_limit = ""
        
        # 首先尝试二进制方式读取文件，检查文件头
        try:
            with open(inf_path, "rb") as f:
                raw_data = f.read()
                # 检查是否有BOM标记
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    content = raw_data[3:].decode('utf-8')
                # 检查是否有其他编码标记
                elif raw_data.startswith(b'\xff\xfe'):
                    content = raw_data[2:].decode('utf-16-le')
                elif raw_data.startswith(b'\xfe\xff'):
                    content = raw_data[2:].decode('utf-16-be')
                else:
                    # 尝试不同的编码
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']:
                        try:
                            content = raw_data.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # 如果所有编码都失败，使用latin1（不会失败，但可能乱码）
                        logger.warning(f"文件 {inf_path} 编码识别失败，使用latin1作为后备")
                        content = raw_data.decode('latin1')
                
                # 解析文件内容
                for line in content.splitlines():
                    line = line.strip()
                    
                    if line.startswith("试题中文名称="):
                        value = line[len("试题中文名称="):].strip()
                        if value.startswith('"') and value.endswith('"'):
                            chinese_name = value[1:-1]
                        else:
                            chinese_name = value.split("//")[0].strip()
                    
                    elif line.startswith("时间限制="):
                        value = line[len("时间限制="):].strip()
                        time_limit = value.split("//")[0].strip()
                    
                    elif line.startswith("内存限制="):
                        value = line[len("内存限制="):].strip()
                        memory_limit = value.split("//")[0].strip()
                
                return ProblemInfo(
                    name=problem_name,
                    chinese_name=chinese_name if chinese_name else problem_name,
                    time_limit=time_limit if time_limit else "1000ms",
                    memory_limit=memory_limit if memory_limit else "256M",
                    data_path=os.path.join(category_path, problem_name),
                    category=os.path.basename(category_path)
                )
        except Exception as e:
            logger.error(f"解析试题信息失败: {str(e)}")
            return None 