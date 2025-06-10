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
        <h3>课程管理</h3>
      </div>

      <div v-if="loading.courses" class="loading">加载中...</div>
      <div v-else-if="courses.length === 0" class="empty-data">
        暂无课程数据
      </div>
      <div v-else class="data-table">
        <table>
          <thead>
            <tr>
              <th>课程名称</th>
              <th>班级</th>
              <th>课程类别</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ course.name }}</td>
              <td>{{ formatClassList(course.classes) }}</td>
              <td>{{ course.category || '未分类' }}</td>
              <td>{{ formatDate(course.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 学生管理 -->
    <div v-else-if="activeTab === 'students'" class="tab-content">
      <div class="content-header">
        <h3>学生管理</h3>
      </div>
      
      <div class="filter-section">
        <div class="filter-item">
          <label for="class-filter">班级筛选：</label>
          <select id="class-filter" v-model="studentFilters.classId" @change="fetchStudents">
            <option value="">全部班级</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="loading.students" class="loading">加载中...</div>
      <div v-else-if="students.length === 0" class="empty-data">
        暂无学生数据
      </div>
      <div v-else class="data-table">
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>学生名称</th>
              <th>班级</th>
              <th>是否在线</th>
              <th>注册时间</th>
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
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from '@/utils/axios';

// 获取路由参数
const route = useRoute();
const router = useRouter();

// 标签页配置
const tabs = [
  { label: '课程管理', value: 'courses' },
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

// 学生筛选
const studentFilters = ref({
  classId: ''
});

// 切换标签
const switchTab = (tab) => {
  activeTab.value = tab;
  // 更新URL参数，但不重新加载页面
  router.push({ 
    path: route.path,
    query: { ...route.query, tab }
  });

  // 根据标签加载相应数据
  loadTabData(tab);
};

// 加载标签数据
const loadTabData = (tab) => {
  switch (tab) {
    case 'courses':
      fetchCourses();
      break;
    case 'students':
      fetchClasses();
      fetchStudents();
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
  if (!classList || classList.length === 0) return '无';
  return classList.map(cls => cls.name).join(', ');
};

// 获取课程列表
const fetchCourses = async () => {
  loading.value.courses = true;
  try {
    const res = await axios.get('/api/courses/');
    courses.value = res.data;
  } catch (error) {
    console.error('获取课程列表失败', error);
    ElMessage.error('获取课程列表失败');
  } finally {
    loading.value.courses = false;
  }
};

// 获取班级列表
const fetchClasses = async () => {
  loading.value.classes = true;
  try {
    const res = await axios.get('/api/classes/');
    classes.value = res.data;
  } catch (error) {
    console.error('获取班级列表失败', error);
    ElMessage.error('获取班级列表失败');
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
    const res = await axios.get(url);
    students.value = res.data;
  } catch (error) {
    console.error('获取学生列表失败', error);
    ElMessage.error('获取学生列表失败');
  } finally {
    loading.value.students = false;
  }
};

// 初始化
onMounted(() => {
  // 根据URL参数初始化当前标签
  if (route.query.tab && tabs.some(tab => tab.value === route.query.tab)) {
    activeTab.value = route.query.tab;
  }
  
  // 加载当前标签数据
  loadTabData(activeTab.value);
});

// 监听路由变化，切换标签
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(tab => tab.value === newTab)) {
    activeTab.value = newTab;
    loadTabData(newTab);
  }
}, { immediate: true });
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
</style> 