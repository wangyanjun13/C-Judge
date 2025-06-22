<template>
  <div class="management-container">
    <div class="page-header">
      <h2>教师管理面板</h2>
    </div>

    <div class="tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.value" 
        :class="['tab-item', { active: activeTab === tab.value }]"
        @click="switchTab(tab.value)"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 课程管理 -->
    <div v-if="activeTab === 'courses'" class="tab-content">
      <div class="content-header">
        <h3>课程竞赛</h3>
      </div>

      <div v-if="loading.courses" class="loading">加载中...</div>
      <div v-else-if="!courses || courses.length === 0" class="empty-data">
        暂无课程数据
      </div>
      <div v-else class="data-table">
        <p>找到 {{ courses.length }} 个课程</p>
        <table>
          <thead>
            <tr>
              <th>课程名称</th>
              <th>教师</th>
              <th>班级</th>
              <th>课程类别</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ course.name }}</td>
              <td>{{ formatTeacherName(course) }}</td>
              <td>
                <span v-if="course.classes && course.classes.length > 0">
                  <span 
                    v-for="(cls, index) in course.classes" 
                    :key="cls.id" 
                    class="class-link"
                    @click="goToStudentsByClass(cls.id)"
                  >
                    {{ cls.name }}{{ index < course.classes.length - 1 ? ', ' : '' }}
                  </span>
                </span>
                <span v-else>无</span>
              </td>
              <td>{{ course.category || '未分类' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 学生管理 -->
    <div v-else-if="activeTab === 'students'" class="tab-content">
      <div class="content-header">
        <h3>学生管理</h3>
        <button class="btn btn-primary" @click="showStudentModal">添加学生</button>
      </div>
      
      <div class="filter-section">
        <div class="filter-item">
          <label for="class-filter">班级筛选：</label>
          <select id="class-filter" v-model="studentFilters.classId" @change="fetchStudents">
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="loading.students" class="loading">加载中...</div>
      <div v-else-if="!students || students.length === 0" class="empty-data">
        暂无学生数据
      </div>
      <div v-else class="data-table">
        <p>找到 {{ students.length }} 个学生</p>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>学生名称</th>
              <th>班级</th>
              <th>是否在线</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, index) in students" :key="student.id">
              <td>{{ index + 1 }}</td>
              <td>{{ student.username }} ({{ student.real_name }})</td>
              <td>{{ formatClassList(student.classes) }}</td>
              <td>
                <span :class="['status-badge', student.is_online ? 'online' : 'offline']">
                  {{ student.is_online ? '在线' : '离线' }}
                </span>
              </td>
              <td>{{ formatDate(student.register_time) }}</td>
              <td>
                <button class="btn btn-sm btn-edit" @click="editStudent(student)">修改</button>
                <button class="btn btn-sm btn-danger" @click="confirmDeleteStudent(student)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 学生添加/编辑对话框 -->
    <div v-if="studentModalVisible" class="modal-overlay" @click="studentModalVisible = false">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑学生' : '添加学生' }}</h3>
        <form @submit.prevent="submitStudentForm">
          <div class="form-group">
            <label for="student-username">用户名（学号）</label>
            <input
              type="text"
              id="student-username"
              v-model="studentForm.username"
              :disabled="isEditing"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="student-password">密码</label>
            <input
              type="password"
              id="student-password"
              v-model="studentForm.password"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="student-confirm-password">确认密码</label>
            <input
              type="password"
              id="student-confirm-password"
              v-model="studentForm.confirmPassword"
              :required="!isEditing"
            />
          </div>
          
          <div class="form-group">
            <label for="student-realname">真实姓名</label>
            <input
              type="text"
              id="student-realname"
              v-model="studentForm.real_name"
              required
            />
          </div>
          
          <div class="form-group">
            <label>班级</label>
            <div class="selected-class">
              {{ getClassName(studentForm.class_ids[0]) || '未选择班级' }}
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="studentModalVisible = false">取消</button>
            <button type="submit" class="btn-primary">{{ isEditing ? '保存' : '添加' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <div v-if="deleteModalVisible" class="modal-overlay" @click="deleteModalVisible = false">
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>您确定要删除学生 "{{ deleteItem?.username }} ({{ deleteItem?.real_name }})" 吗？此操作不可撤销。</p>
        <div class="form-actions">
          <button @click="deleteModalVisible = false">取消</button>
          <button class="btn-danger" @click="confirmDelete">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from '@/utils/axios';
import { logUserOperation, OperationType } from '../../utils/logger';

// 获取路由参数
const route = useRoute();
const router = useRouter();

// 标签页配置
const tabs = [
  { label: '课程竞赛', value: 'courses' },
  { label: '学生管理', value: 'students' }
];

// 当前活动标签
const activeTab = ref(route.query.tab || 'courses');

// 加载状态
const loading = ref({
  courses: false,
  students: false,
  classes: false
});

// 数据
const courses = ref([]);
const students = ref([]);
const classes = ref([]);

// 模态框状态
const studentModalVisible = ref(false);
const deleteModalVisible = ref(false);
const isEditing = ref(false);
const deleteItem = ref(null);

// 学生筛选
const studentFilters = ref({
  classId: ''
});

// 学生表单
const studentForm = ref({
  id: null,
  username: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  role: 'student',
  class_ids: []
});

// 切换标签
const switchTab = async (tab) => {
  activeTab.value = tab;
  // 更新URL参数，但不重新加载页面
  router.push({ 
    path: route.path,
    query: { ...route.query, tab }
  });

  // 根据标签加载相应数据
  await loadTabData(tab);
  
  // 如果是学生管理标签，且班级已加载，设置默认班级
  if (tab === 'students' && classes.value.length > 0 && !studentFilters.value.classId) {
    studentFilters.value.classId = classes.value[0].id;
    fetchStudents();
  }
};

// 加载标签数据
const loadTabData = async (tab) => {
  switch (tab) {
    case 'courses':
      await fetchCourses();
      break;
    case 'students':
      await fetchClasses(); // 先加载班级数据
      await fetchStudents();
      break;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 格式化班级列表
const formatClassList = (classList) => {
  // 确保classList存在且是数组
  if (!classList) return '无';
  try {
    if (Array.isArray(classList)) {
      if (classList.length === 0) return '无';
      // 安全地访问每个班级对象的name属性
      return classList.map(cls => (cls && typeof cls === 'object' && cls.name) ? cls.name : '未命名').join(', ');
    }
    return '无';
  } catch (error) {
    console.error('格式化班级列表出错:', error, '原始数据:', classList);
    return '无';
  }
};

// 获取课程列表
const fetchCourses = async () => {
  loading.value.courses = true;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时
    
    const res = await axios.get('/api/courses/', {
      signal: controller.signal
    }).finally(() => clearTimeout(timeoutId));
    
    if (Array.isArray(res.data)) {
      const rawData = JSON.stringify(res.data);
      courses.value = JSON.parse(rawData);
    } else {
      courses.value = [];
    }
  } catch (error) {
    console.error('获取课程列表失败', error);
    if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
      ElMessage.error('获取课程列表超时，请稍后重试');
    } else {
      ElMessage.error('获取课程列表失败');
    }
    courses.value = [];
  } finally {
    loading.value.courses = false;
  }
};

// 获取班级列表
const fetchClasses = async () => {
  loading.value.classes = true;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时
    
    // 获取当前教师的班级
    const res = await axios.get('/api/classes/teacher', {
      signal: controller.signal
    }).finally(() => clearTimeout(timeoutId));
    
    if (Array.isArray(res.data)) {
      const rawData = JSON.stringify(res.data);
      classes.value = JSON.parse(rawData);
    } else {
      classes.value = [];
    }
  } catch (error) {
    console.error('获取班级列表失败', error);
    if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
      ElMessage.error('获取班级列表超时，请稍后重试');
    } else {
      ElMessage.error('获取班级列表失败');
    }
    classes.value = [];
  } finally {
    loading.value.classes = false;
  }
};

// 获取学生列表
const fetchStudents = async () => {
  loading.value.students = true;
  try {
    let url = '/api/users/students';
    if (studentFilters.value.classId) {
      url += `?class_id=${studentFilters.value.classId}`;
    }
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时
    
    const res = await axios.get(url, {
      signal: controller.signal
    }).finally(() => clearTimeout(timeoutId));
    
    if (Array.isArray(res.data)) {
      const rawData = JSON.stringify(res.data);
      students.value = JSON.parse(rawData);
    } else {
      students.value = [];
    }
  } catch (error) {
    console.error('获取学生列表失败', error);
    if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
      ElMessage.error('获取学生列表超时，请稍后重试');
    } else {
      ElMessage.error('获取学生列表失败');
    }
    students.value = [];
  } finally {
    loading.value.students = false;
  }
};

// 格式化教师名称
const formatTeacherName = (course) => {
  if (course.teacher && course.teacher.username && course.teacher.real_name) {
    return `${course.teacher.username} (${course.teacher.real_name})`;
  } else if (course.teacher_username && course.teacher_real_name) {
    return `${course.teacher_username} (${course.teacher_real_name})`;
  } else if (course.teacher_name) {
    return course.teacher_name;
  }
  return '未分配';
};

// 显示学生编辑对话框
const showStudentModal = () => {
  isEditing.value = false;
  studentForm.value = { 
    id: null, 
    username: '', 
    password: '', 
    confirmPassword: '',
    real_name: '', 
    role: 'student', 
    class_ids: studentFilters.value.classId ? [studentFilters.value.classId] : []
  };
  studentModalVisible.value = true;
};

// 编辑学生
const editStudent = (student) => {
  isEditing.value = true;
  
  studentForm.value = {
    id: student.id,
    username: student.username,
    password: '',
    confirmPassword: '',
    real_name: student.real_name,
    role: 'student',
    class_ids: student.classes && student.classes.length > 0 ? [student.classes[0].id] : []
  };
  studentModalVisible.value = true;
};

// 确认删除学生
const confirmDeleteStudent = (student) => {
  deleteItem.value = student;
  deleteModalVisible.value = true;
};

// 提交学生表单
const submitStudentForm = async () => {
  try {
    if (!studentForm.value.username) {
      ElMessage.warning('请输入用户名');
      return;
    }
    
    if (!isEditing.value) {
      if (!studentForm.value.password) {
        ElMessage.warning('请输入密码');
        return;
      }
      
      if (studentForm.value.password !== studentForm.value.confirmPassword) {
        ElMessage.warning('两次输入的密码不一致');
        return;
      }
    } else if (studentForm.value.password && studentForm.value.password !== studentForm.value.confirmPassword) {
      ElMessage.warning('两次输入的密码不一致');
      return;
    }
    
    if (!studentForm.value.real_name) {
      ElMessage.warning('请输入真实姓名');
      return;
    }
    
    if (!studentForm.value.class_ids || studentForm.value.class_ids.length === 0) {
      ElMessage.warning('请选择班级');
      return;
    }
    
    // 构建提交数据
    const postData = {
      username: studentForm.value.username,
      real_name: studentForm.value.real_name,
      role: 'student',
      class_ids: studentForm.value.class_ids || []
    };
    
    // 只有在创建新学生时才添加密码字段
    if (!isEditing.value) {
      postData.password = studentForm.value.password;
    }
    
    if (isEditing.value) {
      // 更新学生
      await axios.put(`/api/users/student/${studentForm.value.id}`, postData);
      // 记录更新学生操作
      await logUserOperation(OperationType.UPDATE_STUDENT, `学生: ${studentForm.value.real_name} (${studentForm.value.username})`);
      ElMessage.success('学生信息更新成功');
    } else {
      // 创建学生
      await axios.post('/api/users/student', postData);
      // 记录创建学生操作
      await logUserOperation(OperationType.CREATE_STUDENT, `学生: ${studentForm.value.real_name} (${studentForm.value.username})`);
      ElMessage.success('学生创建成功');
    }
    
    studentModalVisible.value = false;
    await fetchStudents();
  } catch (error) {
    console.error('提交学生失败', error);
    // 显示后端返回的错误消息或默认消息
    const errorMsg = error.response?.data?.detail || (isEditing.value ? '更新学生失败' : '创建学生失败');
    ElMessage.error(errorMsg);
  }
};

// 确认删除
const confirmDelete = async () => {
  try {
    // 删除学生
    await axios.delete(`/api/users/student/${deleteItem.value.id}`);
    // 记录删除学生操作
    await logUserOperation(OperationType.DELETE_STUDENT, `学生: ${deleteItem.value.real_name} (${deleteItem.value.username})`);
    ElMessage.success('学生删除成功');
    await fetchStudents();
    deleteModalVisible.value = false;
  } catch (error) {
    console.error('删除失败', error);
    ElMessage.error('删除失败');
  }
};

// 获取班级名称
const getClassName = (classId) => {
  if (!classId) return '';
  const classItem = classes.value.find(cls => cls.id === classId);
  return classItem ? classItem.name : '';
};

// 强制刷新方法
const forceRefresh = async () => {
  await loadTabData(activeTab.value);
};

// 初始化
onMounted(async () => {
  // 检查用户是否已登录
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  // 根据URL参数初始化当前标签
  if (route.query.tab && tabs.some(tab => tab.value === route.query.tab)) {
    activeTab.value = route.query.tab;
  }
  
  // 加载当前标签数据
  await loadTabData(activeTab.value);

  // 如果是学生管理标签，且班级已加载，设置默认班级
  if (activeTab.value === 'students' && classes.value.length > 0) {
    studentFilters.value.classId = classes.value[0].id;
    fetchStudents();
  }
  
  // 延迟后强制刷新一次数据
  setTimeout(forceRefresh, 1000);
});

// 监听路由变化，切换标签
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(tab => tab.value === newTab)) {
    activeTab.value = newTab;
    loadTabData(newTab);
  }
}, { immediate: true });

// 添加班级点击跳转函数
const goToStudentsByClass = (classId) => {
  // 设置学生筛选的班级ID
  studentFilters.value.classId = classId;
  // 切换到学生管理标签
  switchTab('students');
};
</script>

<style scoped>
.management-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-content {
  min-height: 400px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h3 {
  margin: 0;
  color: #303133;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-item label {
  margin-right: 10px;
  font-weight: 500;
}

.filter-item select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-width: 200px;
}

.loading, .empty-data {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.data-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-secondary {
  background-color: #909399;
  color: white;
}

.btn-secondary:hover {
  background-color: #a6a9ad;
}

.btn-edit {
  background-color: #67c23a;
  color: white;
}

.btn-edit:hover {
  background-color: #85ce61;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background-color: #f78989;
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
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #606266;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.form-actions button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button:first-child {
  background-color: #f0f0f0;
  color: #333;
}

.form-actions .btn-primary {
  background-color: #409eff;
  color: white;
}

.form-actions .btn-danger {
  background-color: #f56c6c;
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.online {
  background-color: #67c23a;
  color: white;
}

.offline {
  background-color: #909399;
  color: white;
}

.selected-class {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  color: #606266;
  min-height: 36px;
  line-height: 20px;
}

.class-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}
</style> 