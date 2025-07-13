import { createOperationLog } from '../api/operation_logs';

/**
 * 记录用户操作
 * @param {String} operation - 操作类型
 * @param {String} target - 操作对象
 * @returns {Promise} - 返回创建结果
 */
export const logUserOperation = async (operation, target = null) => {
  // 确保 operation 参数存在
  if (!operation) {
    operation = "未知操作";
  }
  
  try {
    return await createOperationLog(operation, target);
  } catch (error) {
    // 完全隐藏错误，不显示任何信息
    // console.error('记录操作日志失败:', error);
    return { success: false };
  }
};

/**
 * 预定义的操作类型
 */
export const OperationType = {
  // 登录相关
  LOGIN: '登录系统',
  LOGOUT: '退出系统',
  CHANGE_PASSWORD: '修改密码',
  
  // 练习相关
  VIEW_EXERCISE: '查看练习',
  CREATE_EXERCISE: '创建练习',
  UPDATE_EXERCISE: '更新练习',
  DELETE_EXERCISE: '删除练习',
  
  // 题目相关
  VIEW_PROBLEM: '查看题目',
  ADD_PROBLEM: '添加题目',
  REMOVE_PROBLEM: '移除题目',
  UPDATE_PROBLEM: '更新题目',
  UPDATE_PROBLEM_TAGS: '更新题目标签',
  DELETE_PROBLEM: '删除题目',
  UPLOAD_PROBLEM_BANK: '上传题库',
  
  // 提交相关
  SUBMIT_CODE: '提交代码',
  
  // 统计相关
  VIEW_STATISTICS: '查看统计',
  VIEW_ONLINE_USERS: '查看在线用户',
  VIEW_ACTIVE_STUDENTS: '查看在线答题用户',
  
  // 管理相关
  CREATE_STUDENT: '创建学生',
  UPDATE_STUDENT: '更新学生',
  DELETE_STUDENT: '删除学生',
  CREATE_TEACHER: '创建教师',
  UPDATE_TEACHER: '更新教师',
  DELETE_TEACHER: '删除教师',
  CREATE_COURSE: '创建课程',
  UPDATE_COURSE: '更新课程',
  DELETE_COURSE: '删除课程',
  CREATE_CLASS: '创建班级',
  UPDATE_CLASS: '更新班级',
  DELETE_CLASS: '删除班级'
}; 