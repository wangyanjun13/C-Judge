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
  console.log('提交创建练习请求，数据:', JSON.stringify(exerciseData));
  // 确保截止时间有值
  if (!exerciseData.deadline) {
    console.error('截止时间为空，这将导致服务器错误');
    throw new Error('截止时间不能为空');
  }
  
  // 创建一个新对象，将deadline字段转换为end_time
  const apiData = {
    ...exerciseData,
    end_time: exerciseData.deadline
  };
  delete apiData.deadline;
  // 删除note字段
  delete apiData.note;
  
  console.log('转换后的API数据:', JSON.stringify(apiData));
  
  return axios.post('/api/exercises', apiData)
    .then(response => {
      console.log('创建练习成功:', response.data);
      return response.data;
    })
    .catch(error => {
      console.error('创建练习失败:', error.response?.data || error.message);
      throw error;
    });
}

/**
 * 更新练习
 * @param {Number} exerciseId - 练习ID
 * @param {Object} exerciseData - 练习更新数据
 * @returns {Promise} - 返回更新后的练习
 */
export const updateExercise = (exerciseId, exerciseData) => {
  // 创建一个新对象，将deadline字段转换为end_time
  const apiData = {...exerciseData};
  if (apiData.deadline) {
    apiData.end_time = apiData.deadline;
    delete apiData.deadline;
  }
  // 删除note字段
  delete apiData.note;
  
  console.log('更新练习请求，数据:', JSON.stringify(apiData));
  return axios.put(`/api/exercises/${exerciseId}`, apiData);
}

/**
 * 删除练习
 * @param {Number} exerciseId - 练习ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteExercise = (exerciseId) => {
  return axios.delete(`/api/exercises/${exerciseId}`)
}

/**
 * 获取课程列表
 * @returns {Promise} - 返回课程列表
 */
export const getCourses = () => {
  return axios.get('/api/courses')
} 