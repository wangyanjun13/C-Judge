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
    // 延长刷新间隔从30秒到60秒，减少服务器压力
    refreshInterval.value = setInterval(() => {
      // 只有当页面可见且用户活跃时才刷新
      if (!document.hidden && document.hasFocus()) {
        fetchOnlineUsers();
      }
    }, 60000);
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
  padding: 20px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: var(--radius-md);
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: var(--shadow-sm);
  flex-wrap: wrap;
  gap: 16px;
}

.search-box {
  flex-grow: 1;
  margin-right: 16px;
}

.search-box input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  font-size: 14px;
  transition: var(--transition-fast);
  background-color: white;
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-box input:hover {
  border-color: var(--primary-color);
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.role-filter {
  display: flex;
  align-items: center;
  margin-right: 16px;
}

.role-filter label {
  margin-right: 12px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}

.role-filter select {
  padding: 10px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: var(--radius-sm);
  background-color: white;
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
  min-width: 120px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.role-filter select:hover {
  border-color: var(--primary-color);
}

.role-filter select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.btn-refresh {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  cursor: pointer;
  color: var(--primary-color);
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.btn-refresh:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.users-list {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  background: white;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
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

tr:hover {
  background-color: rgba(102, 126, 234, 0.05);
}

tr.inactive {
  opacity: 0.7;
  background-color: #fcfcfc;
}

tr.current-user {
  background-color: rgba(102, 126, 234, 0.1);
}

.current-user-tag {
  margin-left: 5px;
  color: var(--primary-color);
  font-weight: bold;
  background-color: rgba(102, 126, 234, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(102, 126, 234, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
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
  transition: all 0.3s ease;
}

.status-indicator.online {
  background-color: #52c41a;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(82, 196, 26, 0.2);
}

.role-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.role-admin {
  background: linear-gradient(135deg, #409eff, #1677ff);
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
}

.role-teacher {
  background: linear-gradient(135deg, #67c23a, #529b2e);
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.2);
}

.role-student {
  background: linear-gradient(135deg, #e6a23c, #d48806);
  box-shadow: 0 2px 4px rgba(230, 162, 60, 0.2);
}
</style> 