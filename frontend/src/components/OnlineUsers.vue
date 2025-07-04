<template>
  <div class="online-users-container">
    <div class="filter-section">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索用户..." 
          @input="filterUsers"
        />
      </div>
      <div class="role-filter">
        <label>角色筛选：</label>
        <select v-model="selectedRole" @change="filterUsers">
          <option value="">全部</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="admin">管理员</option>
        </select>
      </div>
      <div class="refresh-button">
        <button @click="fetchOnlineUsers" class="btn-refresh" title="刷新">
          <i class="el-icon-refresh"></i>
        </button>
      </div>
    </div>
    
    <div class="users-list">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="!authStore.isAuthenticated" class="empty-state">
        <p>请先登录</p>
      </div>
      <div v-else-if="filteredUsers.length === 0" class="empty-state">
        <p>暂无在线用户</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>角色</th>
            <th>在线状态</th>
            <th>最后活动</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'inactive': !user.is_online, 'current-user': isCurrentUser(user.id) }">
            <td>
              {{ user.username }}
              <span v-if="isCurrentUser(user.id)" class="current-user-tag">(你)</span>
            </td>
            <td>{{ user.real_name || '-' }}</td>
            <td>
              <span class="role-badge" :class="'role-' + user.role">
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td>
              <span class="status-indicator" :class="{ 'online': user.is_online }"></span>
              {{ user.is_online ? '在线' : '离线' }}
            </td>
            <td>{{ formatLastActivity(user.last_activity) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();
const users = ref([]);
const filteredUsers = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const selectedRole = ref('');
const refreshInterval = ref(null);

// 获取当前用户ID
const currentUserId = computed(() => authStore.user?.id);

// 获取在线用户列表
const fetchOnlineUsers = async () => {
  if (!authStore.isAuthenticated) {
    loading.value = false;
    return;
  }
  
  loading.value = true;
  try {
    const response = await authApi.getOnlineUsers();
    users.value = response.data || [];
    filterUsers();
  } catch (error) {
    console.error('获取在线用户失败:', error);
    // 首次加载失败时显示错误
    if (users.value.length === 0) {
      ElMessage.error('无法获取在线用户');
    }
    filterUsers();
  } finally {
    loading.value = false;
  }
};

// 筛选并排序用户
const filterUsers = () => {
  // 筛选用户
  const filtered = users.value.filter(user => {
    // 角色筛选
    if (selectedRole.value && user.role !== selectedRole.value) return false;
    
    // 搜索查询
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      const usernameMatch = user.username.toLowerCase().includes(query);
      const realNameMatch = user.real_name && user.real_name.toLowerCase().includes(query);
      if (!usernameMatch && !realNameMatch) return false;
    }
    
    return true;
  });
  
  // 排序用户：在线用户优先显示
  filteredUsers.value = filtered.sort((a, b) => {
    // 按在线状态排序
    if (a.is_online !== b.is_online) return a.is_online ? -1 : 1;
    
    // 当前用户排在前面
    if (a.id === currentUserId.value) return -1;
    if (b.id === currentUserId.value) return 1;
    
    // 按角色排序
    const roleOrder = { 'admin': 0, 'teacher': 1, 'student': 2 };
    return roleOrder[a.role] - roleOrder[b.role];
  });
};

// 根据角色获取角色名称
const getRoleName = (role) => {
  const roleMap = { 'admin': '管理员', 'teacher': '教师', 'student': '学生' };
  return roleMap[role] || role;
};

// 格式化最后活动时间
const formatLastActivity = (timestamp) => {
  if (!timestamp) return '未知';
  
  try {
    const lastActivity = new Date(timestamp);
    if (isNaN(lastActivity.getTime())) return '未知';
    
    const now = new Date();
    const diffMs = now - lastActivity;
    
    if (diffMs < 60000) return '刚刚';
    if (diffMs < 3600000) return `${Math.floor(diffMs / 60000)}分钟前`;
    if (diffMs < 86400000) return `${Math.floor(diffMs / 3600000)}小时前`;
    
    return lastActivity.toLocaleString('zh-CN', {
      month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  } catch (e) {
    return '时间格式错误';
  }
};

// 判断是否是当前用户
const isCurrentUser = (userId) => userId === currentUserId.value;

// 设置定时刷新
onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchOnlineUsers();
    refreshInterval.value = setInterval(fetchOnlineUsers, 30000);
  } else {
    loading.value = false;
  }
});

// 清除定时器
onUnmounted(() => {
  if (refreshInterval.value) clearInterval(refreshInterval.value);
});
</script>

<style scoped>
.online-users-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.search-box {
  flex-grow: 1;
  margin-right: 16px;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.role-filter {
  display: flex;
  align-items: center;
  margin-right: 16px;
}

.role-filter label {
  margin-right: 8px;
  font-weight: 500;
}

.role-filter select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: white;
}

.btn-refresh {
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  color: #606266;
}

.btn-refresh:hover {
  background-color: #e0e0e0;
}

.users-list {
  flex-grow: 1;
  overflow-y: auto;
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

tr:hover {
  background-color: #f5f7fa;
}

tr.inactive {
  opacity: 0.7;
  background-color: #fcfcfc;
}

tr.current-user {
  background-color: #e6f7ff;
}

.current-user-tag {
  margin-left: 5px;
  color: #1890ff;
  font-weight: bold;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #bbbec4;
  margin-right: 8px;
  vertical-align: middle;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.status-indicator.online {
  background-color: #52c41a;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(82, 196, 26, 0.2);
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
  background-color: #909399;
}

.role-admin {
  background-color: #409eff;
}

.role-teacher {
  background-color: #67c23a;
}

.role-student {
  background-color: #e6a23c;
}
</style> 