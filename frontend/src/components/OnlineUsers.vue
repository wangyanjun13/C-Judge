<template>
  <div class="online-users-container">
    <div class="header">
      <h3>在线用户列表</h3>
      <button @click="refreshUsers" class="refresh-btn">
        <span class="refresh-icon">🔄</span> 刷新
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="onlineUsers.length === 0" class="empty-data">
      <p>暂无在线用户</p>
    </div>
    <div v-else>
      <div class="summary">
        <div class="summary-item">
          <span class="label">在线用户总数：</span>
          <span class="value">{{ onlineUsers.length }}</span>
        </div>
        <div class="summary-item">
          <span class="label">管理员：</span>
          <span class="value">{{ adminCount }}</span>
        </div>
        <div class="summary-item">
          <span class="label">教师：</span>
          <span class="value">{{ teacherCount }}</span>
        </div>
        <div class="summary-item">
          <span class="label">学生：</span>
          <span class="value">{{ studentCount }}</span>
        </div>
      </div>
      
      <table class="online-users-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>角色</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <!-- 管理员 -->
          <template v-if="admins.length > 0">
            <tr class="group-header">
              <td colspan="4">管理员</td>
            </tr>
            <tr v-for="user in admins" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.real_name || user.username }}</td>
              <td>管理员</td>
              <td>
                <span class="badge badge-success">在线</span>
              </td>
            </tr>
          </template>
          
          <!-- 教师 -->
          <template v-if="teachers.length > 0">
            <tr class="group-header">
              <td colspan="4">教师</td>
            </tr>
            <tr v-for="user in teachers" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.real_name || user.username }}</td>
              <td>教师</td>
              <td>
                <span class="badge badge-success">在线</span>
              </td>
            </tr>
          </template>
          
          <!-- 学生 -->
          <template v-if="students.length > 0">
            <tr class="group-header">
              <td colspan="4">学生</td>
            </tr>
            <tr v-for="user in students" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.real_name || user.username }}</td>
              <td>学生</td>
              <td>
                <span class="badge badge-success">在线</span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { authApi } from '../api/auth';
import { ElMessage } from 'element-plus';

const props = defineProps({
  refreshInterval: {
    type: Number,
    default: 30000 // 默认30秒刷新一次
  }
});

const loading = ref(true);
const error = ref(null);
const onlineUsers = ref([]);
const refreshTimer = ref(null);

// 计算不同角色的用户数量
const adminCount = computed(() => admins.value.length);
const teacherCount = computed(() => teachers.value.length);
const studentCount = computed(() => students.value.length);

// 按角色分组用户
const admins = computed(() => onlineUsers.value.filter(user => user.role === 'admin'));
const teachers = computed(() => onlineUsers.value.filter(user => user.role === 'teacher'));
const students = computed(() => onlineUsers.value.filter(user => user.role === 'student'));

// 获取在线用户
const fetchOnlineUsers = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await authApi.getOnlineUsers();
    onlineUsers.value = data;
  } catch (err) {
    console.error('获取在线用户失败:', err);
    error.value = '获取在线用户失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 刷新用户列表
const refreshUsers = () => {
  fetchOnlineUsers();
};

// 设置定时刷新
const setupRefreshInterval = () => {
  refreshTimer.value = setInterval(() => {
    fetchOnlineUsers();
  }, props.refreshInterval);
};

onMounted(() => {
  fetchOnlineUsers();
  setupRefreshInterval();
});

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value);
  }
});
</script>

<style scoped>
.online-users-container {
  width: 100%;
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

.header h3 {
  margin: 0;
  color: #303133;
}

.refresh-btn {
  padding: 6px 12px;
  background-color: #f4f4f5;
  color: #606266;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.refresh-btn:hover {
  background-color: #e9e9eb;
}

.refresh-icon {
  margin-right: 5px;
}

.loading, .error, .empty-data {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.summary {
  display: flex;
  margin-bottom: 15px;
  gap: 20px;
  flex-wrap: wrap;
}

.summary-item {
  background-color: #f5f7fa;
  padding: 10px 15px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.summary-item .label {
  color: #606266;
  margin-right: 8px;
}

.summary-item .value {
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}

.online-users-table {
  width: 100%;
  border-collapse: collapse;
}

.online-users-table th, .online-users-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.online-users-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.group-header {
  background-color: #f0f9eb;
  font-weight: bold;
  color: #67c23a;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-success {
  background-color: #67c23a;
  color: white;
}

.badge-secondary {
  background-color: #909399;
  color: white;
}
</style> 