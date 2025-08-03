<template>
  <div class="exercises-container">
    <div class="header">
      <div class="filter-section">
        <div class="course-selector">
          <label for="course-select">课程：</label>
          <select id="course-select" v-model="selectedCourse">
            <option value="">全部课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="actions">
        <button class="btn btn-primary" @click="showCreateModal">新建练习</button>
        <button class="btn btn-secondary" @click="refreshData">刷新数据</button>
      </div>
    </div>
    
    <div class="exercises-list">
      <table>
        <thead>
          <tr>
            <th>练习名称</th>
            <th>所属课程</th>
            <th>发布时间</th>
            <th>截止时间</th>
            <th>是否在线测评</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="loading-message">加载中...</td>
          </tr>
          <tr v-else-if="filteredExercises.length === 0">
            <td colspan="7" class="empty-message">暂无练习</td>
          </tr>
          <template v-else>
            <tr v-for="exercise in filteredExercises" :key="exercise.id">
              <td>
                <a class="exercise-link" @click="viewExercise(exercise.id)">{{ exercise.name }}</a>
              </td>
              <td>
                <a class="course-link" @click="goToCourseManagement(exercise.course_id)">{{ formatCourseName(exercise) }}</a>
              </td>
              <td>{{ formatDate(exercise.start_time) }}</td>
              <td>{{ formatDate(exercise.end_time) }}</td>
              <td>{{ exercise.is_online_judge ? '是' : '否' }}</td>
              <td>
                <button class="btn btn-edit" @click="showEditModal(exercise)">修改</button>
                <button class="btn btn-danger" @click="confirmDelete(exercise)">删除</button>
                <button class="btn btn-secondary" @click="downloadExercise(exercise.id)">下载</button>
              </td>
              <td>
                <button class="btn btn-text" @click="showNoteModal(exercise)">备注</button>
                <span v-if="exerciseNotes[exercise.id]" class="note-text">{{ exerciseNotes[exercise.id] }}</span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    
    <!-- 创建/编辑练习对话框 -->
    <div v-if="formModalVisible" class="modal-overlay" @click="formModalVisible = false">
      <div class="modal form-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑练习' : '创建练习' }}</h3>
          <button class="close-btn" @click="formModalVisible = false">&times;</button>
        </div>
        <div class="modal-content">
          <form @submit.prevent="submitForm">
            <div class="form-group">
              <label for="exercise-name">练习名称</label>
              <input 
                type="text" 
                id="exercise-name" 
                v-model="form.name" 
                required
              />
            </div>
            
            <div class="form-group">
              <label for="exercise-course">所属课程</label>
              <select 
                id="exercise-course" 
                v-model="form.course_id" 
                required
                :disabled="isEditing"
              >
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="exercise-publisher">发布人</label>
              <input 
                type="text" 
                id="exercise-publisher" 
                :value="getCurrentUserName()"
                disabled
              />
            </div>
            
            <div class="form-group">
              <label for="exercise-start-time">发布时间</label>
              <input 
                type="datetime-local" 
                id="exercise-start-time" 
                v-model="form.start_time"
              />
            </div>
            
            <div class="form-group">
              <label for="exercise-deadline">截止时间</label>
              <div class="datetime-input-wrapper">
                <input 
                  type="datetime-local" 
                  id="exercise-deadline" 
                  v-model="form.deadline"
                  required
                  @change="validateDeadline"
                />
                <div class="datetime-helper">
                  <small>请选择晚于发布时间的截止时间</small>
                </div>
              </div>
            </div>
            
            <div class="form-group checkbox">
              <input 
                type="checkbox" 
                id="exercise-online" 
                v-model="form.is_online_judge"
              />
              <label for="exercise-online">在线测评</label>
            </div>
            
            <div class="form-group">
              <label for="exercise-languages">允许的语言</label>
              <select id="exercise-languages" v-model="form.allowed_languages">
                <option value="c">C语言</option>
                <option value="c,cpp">C/C++</option>
              </select>
            </div>
            
            <div class="form-notice">
              <p class="notice-text">创建练习后需要为练习添加试题：点击[保存]后回到练习列表，点击"练习名称"进入[试题列表]界面，点击[添加]。</p>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" @click="formModalVisible = false">取消</button>
          <button @click="submitForm" class="btn-primary">{{ isEditing ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="deleteModalVisible" class="modal-overlay" @click="deleteModalVisible = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="deleteModalVisible = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>您确定要删除练习 "{{ exerciseToDelete?.name }}" 吗？此操作不可撤销。</p>
        </div>
        <div class="modal-footer">
          <button @click="deleteModalVisible = false">取消</button>
          <button class="btn-danger" @click="deleteExerciseConfirm">删除</button>
        </div>
      </div>
    </div>

    <!-- 添加备注对话框 -->
    <div v-if="noteModalVisible" class="modal-overlay" @click="noteModalVisible = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>练习备注</h3>
          <button class="close-btn" @click="noteModalVisible = false">&times;</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="exercise-note">备注内容</label>
            <textarea 
              id="exercise-note" 
              v-model="exerciseNotes[selectedExercise?.id]" 
              rows="4"
              placeholder="请输入备注内容..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="noteModalVisible = false">关闭</button>
          <button @click="saveNote" class="btn-primary">保存</button>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../../store/auth';
import { 
  getAdminExercises, 
  createExercise, 
  updateExercise, 
  deleteExercise as apiDeleteExercise,
  getCourses
} from '../../api/exercises';
import { logUserOperation, OperationType } from '../../utils/logger';

const router = useRouter();
const exercises = ref([]);
const courses = ref([]);
const loading = ref(true);
const selectedCourse = ref('');
const formModalVisible = ref(false);
const deleteModalVisible = ref(false);
const isEditing = ref(false);
const exerciseToDelete = ref(null);
const noteModalVisible = ref(false);
const selectedExercise = ref(null);
const exerciseNotes = ref({});  // 存储练习的备注，格式为 {exerciseId: noteText}

// 表单数据
const form = ref({
  name: '',
  course_id: '',
  start_time: '',
  deadline: '',
  is_online_judge: true,
  allowed_languages: 'c'
});

// 过滤练习
const filteredExercises = computed(() => {
  let filtered = exercises.value;
  
  // 按课程过滤
  if (selectedCourse.value) {
    filtered = filtered.filter(exercise => exercise.course_id === selectedCourse.value);
  }
  
  return filtered;
});

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化日期为输入框格式
const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 查看练习
const viewExercise = (id) => {
  logUserOperation(OperationType.VIEW_EXERCISE, `练习ID: ${id}`);
  router.push(`/admin/exercise/${id}`);
};

// 刷新数据
const refreshData = () => {
  fetchExercises();
};

// 显示创建对话框
const showCreateModal = () => {
  isEditing.value = false;
  
  // 设置当前时间
  const now = new Date();
  
  // 设置默认截止时间（当前时间一周后）
  const oneWeekLater = new Date(now);
  oneWeekLater.setDate(oneWeekLater.getDate() + 7);
  
  form.value = {
    name: '',
    course_id: courses.value.length > 0 ? courses.value[0].id : '',
    start_time: formatDateForInput(now),
    deadline: formatDateForInput(oneWeekLater),
    is_online_judge: true,
    allowed_languages: 'c'
  };
  formModalVisible.value = true;
};

// 显示编辑对话框
const showEditModal = (exercise) => {
  isEditing.value = true;
  form.value = {
    name: exercise.name,
    course_id: exercise.course_id,
    start_time: exercise.start_time ? formatDateForInput(exercise.start_time) : '',
    deadline: exercise.end_time ? formatDateForInput(exercise.end_time) : '',
    is_online_judge: exercise.is_online_judge,
    allowed_languages: exercise.allowed_languages
  };
  exerciseToDelete.value = exercise;
  formModalVisible.value = true;
};

// 显示删除确认对话框
const confirmDelete = (exercise) => {
  exerciseToDelete.value = exercise;
  deleteModalVisible.value = true;
};

// 获取当前用户名称
const getCurrentUserName = () => {
  const authStore = useAuthStore();
  return authStore.user ? authStore.user.username : '未知用户';
};

// 提交表单
const submitForm = async () => {
  // 检查必填字段
  if (!form.value.name || !form.value.course_id || !form.value.deadline) {
    ElMessage.error('请填写所有必填字段');
    return;
  }
  
  // 确保截止时间晚于发布时间
  validateDeadline();
  
  try {
    if (isEditing.value) {
      // 更新练习
      await updateExercise(exerciseToDelete.value.id, form.value);
      logUserOperation(OperationType.UPDATE_EXERCISE, `练习: ${form.value.name}`);
      ElMessage.success('练习更新成功');
    } else {
      // 创建练习
      await createExercise(form.value);
      logUserOperation(OperationType.CREATE_EXERCISE, `练习: ${form.value.name}`);
      ElMessage.success('练习创建成功');
    }
    formModalVisible.value = false;
    fetchExercises();
  } catch (error) {
    console.error('提交失败', error);
    ElMessage.error(isEditing.value ? '更新练习失败' : '创建练习失败');
  }
};

// 确认删除练习
const deleteExerciseConfirm = async () => {
  if (!exerciseToDelete.value) return;
  
  try {
    await apiDeleteExercise(exerciseToDelete.value.id);
    logUserOperation(OperationType.DELETE_EXERCISE, `练习: ${exerciseToDelete.value.name}`);
    ElMessage.success('练习删除成功');
    deleteModalVisible.value = false;
    fetchExercises();
  } catch (error) {
    console.error('删除失败', error);
    ElMessage.error('删除练习失败');
  }
};

// 获取练习列表
const fetchExercises = async () => {
  loading.value = true;
  try {
    const result = await getAdminExercises();
    
    // 确保返回结果是数组
    exercises.value = Array.isArray(result) ? result : [];
  } catch (error) {
    console.error('获取练习列表失败', error);
    ElMessage.error('获取练习列表失败');
    // 确保在出错时初始化为空数组
    exercises.value = [];
  } finally {
    loading.value = false;
  }
};

// 获取课程列表
const fetchCourses = async () => {
  try {
    const response = await getCourses();
    // 适应不同的API返回格式
    const courseData = Array.isArray(response) ? response : 
                      (response.data && Array.isArray(response.data) ? response.data : []);
    
    courses.value = courseData.map(course => ({
      id: course.id,
      name: course.name
    }));
    
    console.log('获取课程列表成功:', courses.value);
  } catch (error) {
    console.error('获取课程列表失败:', error);
    ElMessage.error('获取课程列表失败');
    courses.value = [];
  }
};

// 下载练习
const downloadExercise = (id) => {
  ElMessage.info('下载功能正在开发中...');
  const exercise = exercises.value.find(e => e.id === id);
  if (exercise) {
    logUserOperation(OperationType.DOWNLOAD_EXERCISE, `练习: ${exercise.name}`);
  } else {
    logUserOperation(OperationType.DOWNLOAD_EXERCISE, `练习ID: ${id}`);
  }
};

// 格式化课程名称
const formatCourseName = (exercise) => {
  if (exercise.course_name && exercise.teacher_name) {
    return `${exercise.course_name}（${exercise.teacher_name}）`;
  } else if (exercise.course_name) {
    return exercise.course_name;
  }
  return '未知课程';
};

// 在script setup部分添加validateDeadline函数
const validateDeadline = () => {
  const startTime = new Date(form.value.start_time);
  const deadline = new Date(form.value.deadline);
  
  if (deadline <= startTime) {
    ElMessage.warning('截止时间必须晚于发布时间');
    // 设置截止时间为发布时间后7天
    const newDeadline = new Date(startTime);
    newDeadline.setDate(newDeadline.getDate() + 7);
    form.value.deadline = formatDateForInput(newDeadline);
  }
};

// 显示备注对话框
const showNoteModal = (exercise) => {
  selectedExercise.value = exercise;
  // 如果本地存储中有该练习的备注，则加载
  const savedNotes = localStorage.getItem('exerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
  noteModalVisible.value = true;
};

// 保存备注
const saveNote = () => {
  if (selectedExercise.value) {
    // 保存到本地存储
    localStorage.setItem('exerciseNotes', JSON.stringify(exerciseNotes.value));
    ElMessage.success('备注保存成功');
    noteModalVisible.value = false;
  }
};

// 在script setup部分添加goToCourseManagement函数
const goToCourseManagement = (courseId) => {
  // 跳转到管理导航栏的课程竞赛模块
  router.push({ 
    path: '/admin/management',
    query: { tab: 'courses' }
  });
};



onMounted(() => {
  fetchExercises();
  fetchCourses();
  
  // 加载备注数据
  const savedNotes = localStorage.getItem('exerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
});
</script>

<style scoped>
.exercises-container {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 24px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  flex-wrap: wrap;
  gap: 16px;
}

.filter-section {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.course-selector, .teacher-selector {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.course-selector label, .teacher-selector label {
  margin-right: 12px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}

.course-selector select, .teacher-selector select {
  padding: 8px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  min-width: 150px;
  background-color: white;
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.course-selector select:hover, .teacher-selector select:hover {
  border-color: var(--primary-color);
}

.course-selector select:focus, .teacher-selector select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: white;
}

th, td {
  padding: 14px 18px;
  text-align: left;
}

th {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

td {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
  font-size: 14px;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: rgba(102, 126, 234, 0.05);
}

.loading-message, .empty-message {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-right: 0;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 2px 5px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #8c8c8c, #6c757d);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-edit {
  background: linear-gradient(135deg, #52c41a, #389e0d);
  color: white;
}

.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(82, 196, 26, 0.3);
}

.btn-danger {
  background: linear-gradient(135deg, #f5222d, #cf1322);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(245, 34, 45, 0.3);
}

.btn-text {
  background: none;
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

.btn-text:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  text-decoration: none;
}

.btn-success {
  background: linear-gradient(135deg, #67c23a, #529b2e);
  color: white;
  box-shadow: 0 2px 5px rgba(103, 194, 58, 0.3);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(103, 194, 58, 0.4);
}

/* 模态对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 增加z-index确保在最顶层 */
}

.modal {
  background: white;
  padding: 0;
  border-radius: var(--radius-lg);
  width: 450px;
  max-width: 90%;
  max-height: 90vh; /* 控制最大高度 */
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: modal-in 0.3s ease;
  display: flex;
  flex-direction: column; /* 使用flex布局 */
}

.form-modal {
  width: 550px;
}

.large-modal {
  width: 800px;
}

.online-users-modal {
  width: 800px;
  max-width: 90%;
  max-height: 90vh; /* 控制最大高度 */
  display: flex;
  flex-direction: column;
}

@keyframes modal-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal h3, .modal-header {
  margin: 0;
  padding: 20px;
  background: var(--primary-gradient);
  color: white;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0; /* 防止头部压缩 */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: none;
  margin-bottom: 0;
}

.modal-header h3 {
  margin: 0;
  padding: 0;
  background: none;
}

.modal-content {
  flex: 1;
  overflow-y: auto; /* 内容区域可滚动 */
  padding: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  font-weight: bold;
  color: white;
  cursor: pointer;
  opacity: 0.8;
  transition: var(--transition-fast);
}

.close-btn:hover {
  opacity: 1;
  color: white;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:first-of-type {
  margin-top: 0; /* 调整顶部边距 */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 14px;
  transition: var(--transition-fast);
}

.form-group input[type="text"]:focus,
.form-group input[type="datetime-local"]:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox input[type="checkbox"] {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
}

.form-group.checkbox label {
  margin-bottom: 0;
  margin-left: 0;
}

.form-notice {
  margin: 0 0 20px;
  padding: 12px;
  background-color: rgba(245, 34, 45, 0.05);
  border: 1px solid rgba(245, 34, 45, 0.2);
  border-radius: var(--radius-sm);
}

.notice-text {
  color: #f5222d;
  margin: 0;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 15px 20px;
  gap: 12px;
  border-top: 1px solid #eee;
  background: #f9f9f9;
  flex-shrink: 0; /* 防止底部按钮区域压缩 */
}

.form-actions button {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition-fast);
}

.form-actions button:first-child {
  background-color: #f0f2f5;
  color: var(--text-primary);
}

.form-actions button:first-child:hover {
  background-color: #e4e6eb;
}

.form-actions .btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.form-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.form-actions .btn-danger {
  background: linear-gradient(135deg, #f5222d, #cf1322);
  color: white;
}

.form-actions .btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(245, 34, 45, 0.3);
}

.exercise-link {
  color: var(--primary-color);
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition-fast);
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: var(--radius-sm);
  display: inline-block;
}

.exercise-link:hover {
  background-color: rgba(102, 126, 234, 0.1);
  text-decoration: none;
}

.course-link {
  color: var(--primary-color);
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition-fast);
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: var(--radius-sm);
  display: inline-block;
}

.course-link:hover {
  background-color: rgba(102, 126, 234, 0.1);
  text-decoration: none;
}

.note-text {
  display: inline-block;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 5px;
  color: var(--text-secondary);
  font-size: 12px;
  font-style: italic;
  background-color: rgba(102, 126, 234, 0.05);
  padding: 2px 6px;
  border-radius: 10px;
}

.datetime-input-wrapper {
  position: relative;
}

.datetime-helper {
  margin-top: 5px;
  color: var(--text-secondary);
  font-size: 12px;
}
</style> 