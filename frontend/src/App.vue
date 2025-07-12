<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue';
import { useAuthStore } from './store/auth';
import { startHeartbeat, stopHeartbeat } from './utils/heartbeat';

const authStore = useAuthStore();

// 初始化认证状态
onMounted(async () => {
  // 优先从会话存储(sessionStorage)中恢复会话，如果没有再尝试从本地存储(localStorage)中恢复
  const token = sessionStorage.getItem('token') || localStorage.getItem('token');
  const userData = sessionStorage.getItem('user') || localStorage.getItem('user');
  
  if (token && userData) {
    try {
      // 确保数据存储在sessionStorage中，以防是从localStorage读取的
      if (!sessionStorage.getItem('token')) {
        sessionStorage.setItem('token', token);
        sessionStorage.setItem('user', userData);
        // 清除localStorage中的数据，防止跨标签页干扰
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      
      // 将数据设置到store中
      authStore.setAuth({
        access_token: token,
        user: JSON.parse(userData)
      });
      
      // 验证会话有效性
      const isSessionValid = await authStore.restoreSession();
      
      // 如果会话有效，启动心跳
      if (isSessionValid) {
        startHeartbeat();
      }
    } catch (error) {
      console.error('会话恢复失败:', error);
      stopHeartbeat();
      // 清除无效的会话数据
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
});

// 监听登录状态变化
watch(() => authStore.isAuthenticated, (newValue) => {
  if (newValue) {
    startHeartbeat();
  } else {
    stopHeartbeat();
  }
});

// 组件卸载时停止心跳检测
onUnmounted(() => {
  stopHeartbeat();
});
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
  color: #303133;
}

#app {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
}

/* 全局过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style> 