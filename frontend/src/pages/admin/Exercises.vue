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
            <th>备注</th>
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
              <td>{{ formatCourseName(exercise) }}</td>
              <td>{{ formatDate(exercise.start_time) }}</td>
              <td>{{ formatDate(exercise.end_time) }}</td>
              <td>{{ exercise.is_online_judge ? '是' : '否' }}</td>
              <td>
                <span class="note-text" :title="exercise.note">{{ exercise.note || '无' }}</span>
              </td>
              <td>
                <button class="btn btn-edit" @click="showEditModal(exercise)">编辑</button>
                <button class="btn btn-danger" @click="confirmDelete(exercise)">删除</button>
                <button class="btn btn-secondary" @click="downloadExercise(exercise.id)">下载</button>
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
            <input 
              type="datetime-local" 
              id="exercise-deadline" 
              v-model="form.deadline"
              required
            />
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
          
          <div class="form-group">
            <label for="exercise-note">备注</label>
            <textarea 
              id="exercise-note" 
              v-model="form.note" 
              rows="4"
            ></textarea>
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

const router = useRouter();
const exercises = ref([]);
const courses = ref([]);
const loading = ref(true);
const selectedCourse = ref('');
const formModalVisible = ref(false);
const deleteModalVisible = ref(false);
const isEditing = ref(false);
const exerciseToDelete = ref(null);

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
  const oneWeekLater = new Date();
  oneWeekLater.setDate(oneWeekLater.getDate() + 7);
  
  form.value = {
    name: '',
    course_id: courses.value.length > 0 ? courses.value[0].id : '',
    start_time: formatDateForInput(now),
    deadline: formatDateForInput(oneWeekLater),
    is_online_judge: true,
    allowed_languages: 'c',
    note: ''
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
    deadline: exercise.deadline ? formatDateForInput(exercise.deadline) : '',
    is_online_judge: exercise.is_online_judge,
    allowed_languages: exercise.allowed_languages,
    note: exercise.note || ''
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
  
  try {
    if (isEditing.value) {
      // 更新练习
      await updateExercise(exerciseToDelete.value.id, form.value);
      ElMessage.success('练习更新成功');
    } else {
      // 创建练习
      await createExercise(form.value);
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

onMounted(() => {
  fetchExercises();
  fetchCourses();
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

.filter-section {
  display: flex;
  gap: 20px;
}

.course-selector, .teacher-selector {
  display: flex;
  align-items: center;
}

.course-selector label, .teacher-selector label {
  margin-right: 10px;
  font-weight: 500;
}

.course-selector select, .teacher-selector select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 150px;
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

.btn-secondary {
  background-color: #8c8c8c;
  color: white;
}

.btn-secondary:hover {
  background-color: #a6a6a6;
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

.note-text {
  display: inline-block;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 