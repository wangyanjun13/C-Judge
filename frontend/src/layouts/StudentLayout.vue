<template>
  <div class="layout">
    <header class="header">
      <div class="logo">Just For Fun-测评系统(C语言)</div>
      <nav class="nav">
        <router-link to="/student/exercises" class="nav-item">练习</router-link>
        <router-link to="/student/operation-logs" class="nav-item">操作记录</router-link>
        <div class="dropdown">
          <button class="nav-item dropdown-btn">系统</button>
          <div class="dropdown-content">
            <router-link to="/student/profile" class="dropdown-item">修改密码</router-link>
            <div class="dropdown-item" @click="showAbout">关于</div>
            <div class="dropdown-item" @click="handleLogout">退出</div>
          </div>
        </div>
      </nav>
      <div class="center-buttons">
        <button class="center-btn" @click="goToMySubmissions">        
          <img src="/个人仪表盘.svg" alt="仪表盘" class="dashboard-icon" />
          个人面板
        </button>
      </div>
      <div class="user-info">
        <span>{{ user?.real_name || user?.username }}</span>
      </div>
    </header>
    
    <main class="main-content">
      <router-view></router-view>
    </main>
    
    <!-- 页脚 -->
    <Footer />
    
    <!-- 关于对话框 -->
    <div v-if="aboutVisible" class="modal-overlay" @click="aboutVisible = false">
      <div class="modal" @click.stop>
        <h2>关于系统</h2>
        <p>本系统为用于教育场景的C语言在线测评平台，主要用于C语言教学，支持C语言的在线测评，支持C语言的在线提交、在线测评、在线查看结果，支持教师管理、学生管理、班级管理、课程管理、题库管理、评测管理等，支持用户管理、权限管理、日志管理等，支持系统设置、统计数据等。</p>
        <p>版本：1.0.0</p>
        <p>联系开发者：wangyanjun13@foxmail.com</p>
        <button @click="aboutVisible = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import Footer from '../components/Footer.vue';

const router = useRouter();
const authStore = useAuthStore();
const aboutVisible = ref(false);

// 获取用户信息
const user = computed(() => authStore.user);

// 显示关于对话框
const showAbout = () => {
  aboutVisible.value = true;
};

// 处理登出
const handleLogout = async () => {
  await authStore.logout();
  router.push('/login');
};

const goToMySubmissions = () => {
  router.push('/my-submissions');
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

.center-buttons {
  display: flex;
  align-items: center;
  margin-right: 20px;
  margin-left: auto;
}

.center-btn {
  padding: 6px 16px;
  background: none;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.center-btn:hover {
  transform: translateY(-1px);
}

.dashboard-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
}
</style> 