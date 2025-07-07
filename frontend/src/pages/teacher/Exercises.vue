<template>
  <div class="exercises-container">
    <div class="header">
      <div class="course-selector">
        <label for="course-select">课程：</label>
        <select id="course-select" v-model="selectedCourse">
          <option value="">全部课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
      <div class="actions">
        <button class="btn btn-success" @click="showOnlineUsersModal">
          <i class="el-icon-user"></i> 在线用户
        </button>
        <button class="btn btn-primary" @click="showCreateModal">新建练习</button>
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
          <tr v-else-if="exercises.length === 0">
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
        <h3>{{ isEditing ? '编辑练习' : '创建练习' }}</h3>
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
          
          <div class="form-actions">
            <button type="button" @click="formModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="deleteModalVisible" class="modal-overlay" @click="deleteModalVisible = false">
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>您确定要删除练习 "{{ exerciseToDelete?.name }}" 吗？此操作不可撤销。</p>
        <div class="form-actions">
          <button @click="deleteModalVisible = false">取消</button>
          <button class="btn-danger" @click="deleteExerciseConfirm">删除</button>
        </div>
      </div>
    </div>

    <!-- 添加备注对话框 -->
    <div v-if="noteModalVisible" class="modal-overlay" @click="noteModalVisible = false">
      <div class="modal" @click.stop>
        <h3>练习备注</h3>
        <div class="form-group">
          <label for="exercise-note">备注内容</label>
          <textarea 
            id="exercise-note" 
            v-model="exerciseNotes[selectedExercise?.id]" 
            rows="4"
            placeholder="请输入备注内容..."
          ></textarea>
        </div>
        <div class="form-actions">
          <button @click="noteModalVisible = false">关闭</button>
          <button @click="saveNote" class="btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 在线用户对话框 -->
    <div v-if="onlineUsersModalVisible" class="modal-overlay" @click="closeOnlineUsersModal">
      <div class="modal online-users-modal" @click.stop>
        <div class="modal-header">
          <h3>在线用户列表</h3>
          <button class="close-btn" @click="closeOnlineUsersModal">×</button>
        </div>
        <OnlineUsers />
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
  getTeacherExercises, 
  createExercise, 
  updateExercise, 
  deleteExercise as apiDeleteExercise,
  getCourses
} from '../../api/exercises';
import { logUserOperation, OperationType } from '../../utils/logger';
import OnlineUsers from '../../components/OnlineUsers.vue';

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
const onlineUsersModalVisible = ref(false);

// 表单数据
const form = ref({
  name: '',
  course_id: '',
  start_time: '',
  deadline: '',
  is_online_judge: true,
  allowed_languages: 'c',
  note: ''
});

// 过滤练习
const filteredExercises = computed(() => {
  if (!selectedCourse.value) {
    return exercises.value;
  }
  return exercises.value.filter(exercise => exercise.course_id === selectedCourse.value);
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
  router.push(`/teacher/exercise/${id}`);
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
      // 记录更新练习操作
      await logUserOperation(OperationType.UPDATE_EXERCISE, `练习: ${form.value.name}`);
      ElMessage.success('练习更新成功');
    } else {
      // 创建练习
      const result = await createExercise(form.value);
      // 记录创建练习操作
      await logUserOperation(OperationType.CREATE_EXERCISE, `练习: ${form.value.name}`);
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
    // 记录删除练习操作
    await logUserOperation(OperationType.DELETE_EXERCISE, `练习: ${exerciseToDelete.value.name}`);
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
    const result = await getTeacherExercises();
    
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

// 添加跳转到课程管理的函数
const goToCourseManagement = (courseId) => {
  // 跳转到教师管理导航栏的课程竞赛模块
  router.push({ 
    path: '/teacher/management',
    query: { tab: 'courses' }
  });
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
  const savedNotes = localStorage.getItem('teacherExerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
  noteModalVisible.value = true;
};

// 保存备注
const saveNote = () => {
  if (selectedExercise.value) {
    // 保存到本地存储
    localStorage.setItem('teacherExerciseNotes', JSON.stringify(exerciseNotes.value));
    ElMessage.success('备注保存成功');
    noteModalVisible.value = false;
  }
};

// 显示在线用户对话框
const showOnlineUsersModal = () => {
  onlineUsersModalVisible.value = true;
  // 记录查看在线用户的操作
  logUserOperation(OperationType.VIEW_ONLINE_USERS, "查看在线用户列表").catch(err => {
    console.warn('记录操作失败:', err);
  });
};

// 关闭在线用户对话框
const closeOnlineUsersModal = () => {
  onlineUsersModalVisible.value = false;
};

onMounted(() => {
  fetchExercises();
  fetchCourses();
  
  // 加载备注数据
  const savedNotes = localStorage.getItem('teacherExerciseNotes');
  if (savedNotes) {
    exerciseNotes.value = JSON.parse(savedNotes);
  }
});
</script>

<style scoped>
.exercises-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.course-selector {
  display: flex;
  align-items: center;
}

.course-selector label {
  margin-right: 10px;
  font-weight: 500;
}

.course-selector select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 200px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

th {
  background-color: #fafafa;
  font-weight: 500;
}

.loading-message, .empty-message {
  text-align: center;
  padding: 20px;
  color: #999;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-edit {
  background-color: #52c41a;
  color: white;
}

.btn-edit:hover {
  background-color: #73d13d;
}

.btn-danger {
  background-color: #f5222d;
  color: white;
}

.btn-danger:hover {
  background-color: #ff4d4f;
}

.btn-secondary {
  background-color: #909399;
  color: white;
}

.btn-secondary:hover {
  background-color: #a6a9ad;
}

/* 备注按钮样式 */
.btn-text {
  background: none;
  border: none;
  color: #1890ff;
  cursor: pointer;
  padding: 0;
}

.btn-text:hover {
  text-decoration: underline;
  color: #40a9ff;
}

/* 模态对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.form-modal {
  width: 500px;
}

.modal h3 {
  margin-top: 0;
  color: #1890ff;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox label {
  margin-bottom: 0;
  margin-left: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.form-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.form-actions button:first-child {
  background-color: #f0f0f0;
  color: #333;
}

.form-actions .btn-primary {
  background-color: #1890ff;
  color: white;
}

.form-actions .btn-danger {
  background-color: #f5222d;
  color: white;
}

.form-notice {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
}

.notice-text {
  color: #f5222d;
  margin: 0;
  font-size: 14px;
}

.exercise-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.exercise-link:hover {
  text-decoration: underline;
}

.course-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.course-link:hover {
  text-decoration: underline;
}

.note-text {
  display: inline-block;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 5px;
  color: #999;
  font-size: 12px;
  font-style: italic;
}

.datetime-input-wrapper {
  position: relative;
}

.datetime-helper {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.online-users-modal {
  width: 800px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.modal-header h3 {
  margin: 0;
  color: #1890ff;
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  font-weight: bold;
  color: #909399;
  cursor: pointer;
}

.close-btn:hover {
  color: #f56c6c;
}

.btn-info {
  background-color: #909399;
  color: white;
}

.btn-info:hover {
  background-color: #a6a9ad;
}

.btn-success {
  background-color: #67c23a;
  color: white;
}

.btn-success:hover {
  background-color: #85ce61;
}

.online-users-btn {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style> 