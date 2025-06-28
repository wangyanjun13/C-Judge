<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useAuthStore } from './store/auth';
import { authApi } from './api/auth';

const authStore = useAuthStore();
const heartbeatInterval = ref(null);

// 设置心跳
const setupHeartbeat = () => {
  // 清除之前的心跳
  if (heartbeatInterval.value) {
    clearInterval(heartbeatInterval.value);
  }
  
  // 每60秒发送一次心跳
  heartbeatInterval.value = setInterval(() => {
    // 只有登录状态下才发送心跳
    if (authStore.isLoggedIn) {
      authApi.sendHeartbeat();
    }
  }, 60000); // 60秒
};

onMounted(() => {
  setupHeartbeat();
});

onUnmounted(() => {
  if (heartbeatInterval.value) {
    clearInterval(heartbeatInterval.value);
  }
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