import axios from '../utils/axios'

/**
 * 提交代码
 * @param {Number} userId - 用户ID
 * @param {Number} problemId - 题目ID
 * @param {Number} exerciseId - 练习ID（可选）
 * @param {String} code - 代码内容
 * @param {String} language - 编程语言
 * @returns {Promise} - 返回提交结果
 */
export const submitCode = (userId, problemId, exerciseId, code, language) => {
  const data = {
    user_id: userId,
    problem_id: problemId,
    exercise_id: exerciseId,
    code: code,
    language: language
  };
  
  return axios.post('/api/submissions', data)
    .then(response => {
      return response.data;
    })
    .catch(error => {
      console.error('提交代码失败:', error);
      // 提取错误信息
      const errorMsg = error.response?.data?.detail || '提交失败，请稍后重试';
      throw new Error(errorMsg);
    });
}

/**
 * 获取提交记录详情
 * @param {Number} submissionId - 提交记录ID
 * @returns {Promise} - 提交记录详情
 */
export const getSubmissionDetail = async (submissionId) => {
  try {
    const response = await axios.get(`/api/submissions/${submissionId}`);
    return response.data;
  } catch (error) {
    console.error('获取提交记录详情失败:', error);
    throw error;
  }
}

/**
 * 获取提交记录列表
 * @param {Object} filters - 筛选条件
 * @param {Number} filters.userId - 用户ID
 * @param {Number} filters.problemId - 问题ID
 * @param {Number} filters.exerciseId - 练习ID
 * @returns {Promise} - 提交记录列表
 */
export const getSubmissions = async (filters = {}) => {
  try {
    const { userId, problemId, exerciseId } = filters;
    
    let url = '/api/submissions?';
    if (userId) url += `user_id=${userId}&`;
    if (problemId) url += `problem_id=${problemId}&`;
    if (exerciseId) url += `exercise_id=${exerciseId}&`;
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('获取提交记录列表失败:', error);
    throw error;
  }
} 