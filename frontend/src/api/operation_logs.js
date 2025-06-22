import axios from '../utils/axios'

/**
 * 获取当前用户的操作日志
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回操作日志列表
 */
export const getUserOperationLogs = async (params = {}) => {
  try {
    const response = await axios.get('/api/operation-logs', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取操作日志失败:', error);
    return [];
  }
}

/**
 * 创建操作日志
 * @param {String} operation - 操作类型
 * @param {String} target - 操作对象
 * @returns {Promise} - 返回创建结果
 */
export const createOperationLog = async (operation, target = null) => {
  // 确保 operation 参数存在，如果不存在则提供默认值
  if (!operation) {
    operation = "未知操作";
  }
  
  try {
    const response = await axios.post('/api/operation-logs', null, { 
      params: { operation, target } 
    });
    return response.data;
  } catch (error) {
    // 完全隐藏错误，不显示任何信息
    // console.error('创建操作日志失败:', error);
    return { success: false };
  }
}

/**
 * 清空当前用户的所有操作日志
 * @returns {Promise} - 返回清空结果
 */
export const clearAllOperationLogs = async () => {
  try {
    const response = await axios.delete('/api/operation-logs');
    return response.data;
  } catch (error) {
    console.error('清空操作日志失败:', error);
    throw error; // 这里需要抛出异常，因为清空是用户主动操作，需要反馈结果
  }
} 