import axios from '../utils/axios'

/**
 * 获取学生练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getStudentExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/student', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取学生练习列表失败:', error);
    return [];
  }
}

/**
 * 获取教师练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getTeacherExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/teacher', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取教师练习列表失败:', error);
    return [];
  }
}

/**
 * 获取管理员练习列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回练习列表
 */
export const getAdminExercises = async (params = {}) => {
  try {
    const response = await axios.get('/api/exercises/admin', { params });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('获取管理员练习列表失败:', error);
    return [];
  }
}

/**
 * 获取练习详情
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回练习详情
 */
export const getExerciseDetail = (exerciseId) => {
  return axios.get(`/api/exercises/${exerciseId}`)
}

/**
 * 创建练习
 * @param {Object} exerciseData - 练习数据
 * @returns {Promise} - 返回创建的练习
 */
export const createExercise = (exerciseData) => {
  return axios.post('/api/exercises', exerciseData)
}

/**
 * 更新练习
 * @param {Number} exerciseId - 练习ID
 * @param {Object} exerciseData - 练习更新数据
 * @returns {Promise} - 返回更新后的练习
 */
export const updateExercise = (exerciseId, exerciseData) => {
  return axios.put(`/api/exercises/${exerciseId}`, exerciseData)
}

/**
 * 删除练习
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteExercise = (exerciseId) => {
  return axios.delete(`/api/exercises/${exerciseId}`)
} 