<template>
  <div class="layout">
    <header class="header">
      <div class="logo">C语言评测系统</div>
      <nav class="nav">
        <router-link to="/teacher/exercises" class="nav-item">练习</router-link>
        <router-link to="/teacher/operation-logs" class="nav-item">操作记录</router-link>
        
        <div class="dropdown">
          <button class="nav-item dropdown-btn">管理</button>
          <div class="dropdown-content">
            <router-link to="/teacher/management?tab=courses" class="dropdown-item">课程竞赛</router-link>
            <router-link to="/teacher/management?tab=students" class="dropdown-item">学生管理</router-link>
          </div>
        </div>
        
        <div class="dropdown">
          <button class="nav-item dropdown-btn">维护</button>
          <div class="dropdown-content">
            <router-link to="/teacher/maintenance?tab=upload" class="dropdown-item">上传题库</router-link>
            <router-link to="/teacher/maintenance?tab=problems" class="dropdown-item">题库维护</router-link>
          </div>
        </div>
        
        <div class="dropdown">
          <button class="nav-item dropdown-btn">系统</button>
          <div class="dropdown-content">
            <router-link to="/teacher/profile" class="dropdown-item">修改密码</router-link>
            <div class="dropdown-item" @click="showAbout">关于</div>
            <div class="dropdown-item" @click="showHelp">帮助</div>
            <div class="dropdown-item" @click="handleLogout">退出</div>
          </div>
        </div>
      </nav>
      <div class="user-info">
        <span>{{ user?.real_name || user?.username }}</span>
      </div>
    </header>
    
    <main class="main-content">
      <router-view></router-view>
    </main>
    
    <!-- 关于对话框 -->
    <div v-if="aboutVisible" class="modal-overlay" @click="aboutVisible = false">
      <div class="modal" @click.stop>
        <h2>关于系统</h2>
        <p>本系统为用于教育场景的C语言在线评测平台。</p>
        <p>版本：1.0.0</p>
        <p>开发者：wangyanjun13@foxmail.com</p>
        <button @click="aboutVisible = false">关闭</button>
      </div>
    </div>
    
    <!-- 帮助对话框 -->
    <div v-if="helpVisible" class="modal-overlay" @click="helpVisible = false">
      <div class="modal" @click.stop>
        <h2>系统帮助</h2>
        <p>C语言评测系统使用指南：</p>
        <ul>
          <li>练习：查看和管理课程练习</li>
          <li>操作记录：查看系统操作日志</li>
          <li>管理：管理课程和学生</li>
          <li>维护：上传和维护题库</li>
        </ul>
        <button @click="helpVisible = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();
const aboutVisible = ref(false);
const helpVisible = ref(false);

// 获取用户信息
const user = computed(() => authStore.user);

// 显示关于对话框
const showAbout = () => {
  aboutVisible.value = true;
};

// 显示帮助对话框
const showHelp = () => {
  helpVisible.value = true;
};

// 处理登出
const handleLogout = async () => {
  await authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #1890ff;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 40px;
}

.nav {
  display: flex;
  flex-grow: 1;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 0 20px;
  line-height: 60px;
  cursor: pointer;
}

.nav-item:hover {
  background-color: #40a9ff;
}

.user-info {
  margin-left: 20px;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
  background-color: #f0f2f5;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-btn {
  border: none;
  background: none;
  font-size: 16px;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #fff;
  min-width: 160px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-item {
  color: #333;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f1f1f1;
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

.modal h2 {
  margin-top: 0;
  color: #1890ff;
}

.modal button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal button:hover {
  background-color: #40a9ff;
}
</style> 