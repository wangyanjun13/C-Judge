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
  // 从本地存储中尝试恢复会话
  const token = localStorage.getItem('token');
  const userData = localStorage.getItem('user');
  
  if (token && userData) {
    try {
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