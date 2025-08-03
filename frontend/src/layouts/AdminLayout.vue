<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🎯</span>
          <span class="logo-text">Just For Fun</span>
          <span class="logo-subtitle">C语言测评系统</span>
        </div>
        
      <nav class="nav">
        <router-link to="/admin/exercises" class="nav-item">
          <img src="/代码.svg" alt="练习" class="nav-icon" />
          <span>练习</span>
        </router-link>
        <router-link to="/admin/operation-logs" class="nav-item">
          <img src="/记录.svg" alt="操作记录" class="nav-icon" />
          <span>操作记录</span>
        </router-link>
        
          <div class="dropdown" ref="managementDropdown">
            <button class="nav-item dropdown-btn" @click="toggleDropdown('management', $event)" @mouseenter="showDropdown('management')">
            <img src="/管理.svg" alt="管理" class="nav-icon" />
            <span>管理</span>
              <span class="dropdown-arrow" :class="{ 'open': activeDropdown === 'management' }">▼</span>
          </button>
            <div class="dropdown-content modern-dropdown" :class="{ 'show': activeDropdown === 'management' }" @mouseenter="keepDropdown('management')" @mouseleave="closeDropdown">
              <router-link to="/admin/management?tab=classes" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">🏫</span>班级管理
              </router-link>
              <router-link to="/admin/management?tab=teachers" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">👨‍🏫</span>教师管理
              </router-link>
              <router-link to="/admin/management?tab=courses" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">📚</span>课程竞赛
              </router-link>
              <router-link to="/admin/management?tab=students" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">👨‍🎓</span>学生管理
              </router-link>
          </div>
        </div>
        
          <div class="dropdown" ref="maintenanceDropdown">
            <button class="nav-item dropdown-btn" @click="toggleDropdown('maintenance', $event)" @mouseenter="showDropdown('maintenance')">
            <img src="/维护.svg" alt="维护" class="nav-icon" />
            <span>维护</span>
              <span class="dropdown-arrow" :class="{ 'open': activeDropdown === 'maintenance' }">▼</span>
          </button>
            <div class="dropdown-content modern-dropdown" :class="{ 'show': activeDropdown === 'maintenance' }" @mouseenter="keepDropdown('maintenance')" @mouseleave="closeDropdown">
              <router-link to="/admin/maintenance?tab=upload" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">📤</span>上传题库
              </router-link>
              <router-link to="/admin/maintenance?tab=problems" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">🔧</span>题库维护
              </router-link>
              <router-link to="/admin/maintenance?tab=tags" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">🏷️</span>标签管理
              </router-link>
              <router-link to="/admin/maintenance?tab=approval" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">✅</span>标签审核
              </router-link>
            </div>
          </div>
          
          <div class="dropdown" ref="systemDropdown">
            <button class="nav-item dropdown-btn" @click="toggleDropdown('system', $event)" @mouseenter="showDropdown('system')">
              <img src="/个人仪表盘.svg" alt="系统" class="nav-icon" />
              <span>系统</span>
              <span class="dropdown-arrow" :class="{ 'open': activeDropdown === 'system' }">▼</span>
            </button>
            <div class="dropdown-content modern-dropdown" :class="{ 'show': activeDropdown === 'system' }" @mouseenter="keepDropdown('system')" @mouseleave="closeDropdown">
              <router-link to="/admin/system?tab=password" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">🔐</span>修改密码
              </router-link>
              <router-link to="/admin/system?tab=settings" class="dropdown-item modern-dropdown-item" @click="closeDropdown">
                <span class="item-icon">⚙️</span>系统设置
              </router-link>
              <div class="dropdown-item modern-dropdown-item" @click="showHelp">
                <span class="item-icon">❓</span>帮助
              </div>
              <div class="dropdown-item modern-dropdown-item" @click="showAbout">
                <span class="item-icon">ℹ️</span>关于
              </div>
              <div class="dropdown-item modern-dropdown-item logout-item" @click="handleLogout">
                <span class="item-icon">🚪</span>退出
              </div>
          </div>
        </div>
        </nav>
        
        <div class="header-actions">
          <button class="online-users-btn glass-effect" @click="showOnlineUsersModal">
            <span class="online-icon">👥</span>
            <span>在线用户</span>
          </button>
          
          <button class="dashboard-btn glass-effect" @click="goToMySubmissions">
            <img src="/个人仪表盘.svg" alt="仪表盘" class="dashboard-icon" />
            <span>个人面板</span>
          </button>
          
          <div class="user-info glass-effect">
            <div class="user-avatar">{{ (user?.real_name || user?.username)?.[0]?.toUpperCase() }}</div>
            <div class="user-details">
              <div class="user-name">{{ user?.real_name || user?.username }}</div>
              <div class="user-role">管理员</div>
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <main class="main-content">
      <router-view></router-view>
    </main>
    
    <!-- 页脚 -->
    <Footer />
    
    <!-- 在线用户对话框 -->
    <div v-if="onlineUsersModalVisible" class="modal-overlay" @click="closeOnlineUsersModal">
      <div class="modal large-modal glass-effect" @click.stop>
        <div class="modal-header">
          <h2>在线用户列表</h2>
          <button class="close-btn" @click="closeOnlineUsersModal">✕</button>
        </div>
        <div class="modal-content">
          <OnlineUsers />
        </div>
        <div class="modal-footer">
          <button @click="closeOnlineUsersModal" class="btn-primary">关闭</button>
        </div>
      </div>
    </div>
    
    <!-- 关于对话框 -->
    <div v-if="aboutVisible" class="modal-overlay" @click="aboutVisible = false">
      <div class="modal glass-effect" @click.stop>
        <div class="modal-header">
        <h2>关于系统</h2>
          <button class="close-btn" @click="aboutVisible = false">✕</button>
        </div>
        <div class="modal-content">
        <p>本系统为用于教育场景的简单C语言在线测评平台，主要用于C语言教学，支持C语言的在线评测，支持C语言的在线提交、在线评测、在线查看结果，支持教师管理、学生管理、班级管理、课程管理、题库管理、评测管理等，支持用户管理、权限管理、日志管理等，支持系统设置、统计数据等。</p>
          <p><strong>版本：</strong>1.0.0</p>
          <p><strong>联系开发者：</strong>wangyanjun13@foxmail.com</p>
        </div>
      </div>
    </div>
    
    <!-- 帮助对话框 -->
    <div v-if="helpVisible" class="modal-overlay" @click="helpVisible = false">
      <div class="modal glass-effect" @click.stop>
        <div class="modal-header">
        <h2>系统帮助</h2>
          <button class="close-btn" @click="helpVisible = false">✕</button>
        </div>
        <div class="modal-content">
          <p><strong>C语言评测系统使用指南：</strong></p>
          <ul class="help-list">
            <li><span class="help-icon">📝</span>练习：查看和管理课程练习</li>
            <li><span class="help-icon">📋</span>操作记录：查看系统操作日志</li>
            <li><span class="help-icon">👥</span>管理：管理班级、教师、课程和学生</li>
            <li><span class="help-icon">🔧</span>维护：上传和维护题库</li>
            <li><span class="help-icon">⚙️</span>系统：系统设置和统计数据</li>
        </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import Footer from '../components/Footer.vue';
import OnlineUsers from '../components/OnlineUsers.vue';
import { logUserOperation, OperationType } from '../utils/logger';

const router = useRouter();
const authStore = useAuthStore();
const aboutVisible = ref(false);
const helpVisible = ref(false);
const onlineUsersModalVisible = ref(false); // Added state for online users modal

// 下拉菜单状态
const activeDropdown = ref(null);

// 获取用户信息
const user = computed(() => authStore.user);

// 切换下拉菜单
const toggleDropdown = (dropdownName, event) => {
  event.stopPropagation();
  activeDropdown.value = activeDropdown.value === dropdownName ? null : dropdownName;
};

// 显示下拉菜单
const showDropdown = (dropdownName) => {
  activeDropdown.value = dropdownName;
};

// 保持下拉菜单显示
const keepDropdown = (dropdownName) => {
  activeDropdown.value = dropdownName;
};

// 关闭下拉菜单
const closeDropdown = () => {
  activeDropdown.value = null;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (activeDropdown.value) {
    activeDropdown.value = null;
  }
};

// 显示关于对话框
const showAbout = () => {
  aboutVisible.value = true;
  closeDropdown();
};

// 显示帮助对话框
const showHelp = () => {
  helpVisible.value = true;
  closeDropdown();
};

// 处理登出
const handleLogout = async () => {
  closeDropdown();
  await authStore.logout();
  router.push('/login');
};

const goToMySubmissions = () => {
  router.push('/my-submissions');
};

// 显示在线用户对话框
const showOnlineUsersModal = () => {
  onlineUsersModalVisible.value = true;
  closeDropdown();
  // 记录查看在线用户的操作
  logUserOperation(OperationType.VIEW_ONLINE_USERS, "查看在线用户列表").catch(err => {
    console.warn('记录操作失败:', err);
  });
};

// 关闭在线用户对话框
const closeOnlineUsersModal = () => {
  onlineUsersModalVisible.value = false;
};

// 组件挂载时添加全局点击监听
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

// 组件卸载时移除监听
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-pri mary);
}

.header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: var(--primary-gradient);
  color: white;
  box-shadow: var(--shadow-md);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  color: var(--text-white);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  color: var(--text-white);
}

.logo-subtitle {
  font-size: 14px;
  color: var(--text-light);
}

.nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-item {
  color: var(--text-white);
  text-decoration: none;
  padding: 8px 15px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  transition: var(--transition-fast);
}

.nav-item:hover {
  background: var(--bg-hover);
}

.nav-icon {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1);
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-btn {
  border: none;
  background: none;
  color: var(--text-white);
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 15px;
  border-radius: var(--radius-sm);
  transition: var(--transition-fast);
}

.dropdown-btn:hover {
  background: var(--bg-hover);
}

.dropdown-arrow {
  margin-left: 4px;
  font-size: 10px;
  transition: var(--transition-fast);
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-content {
  display: none;
  position: absolute;
  background: var(--bg-secondary);
  min-width: 200px;
  box-shadow: var(--shadow-lg);
  z-index: 9999;
  border-radius: var(--radius-md);
  padding: 8px 0;
  margin-top: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  right: 0;
  pointer-events: auto;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.dropdown-content.show {
  display: block;
  opacity: 1;
  transform: translateY(0);
  pointer-events: all; /* 确保可以点击 */
}

.modern-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
  border-bottom: 1px solid #f1f5f9;
  position: relative;
  z-index: 10000;
  pointer-events: auto;
}

.modern-dropdown-item:last-child {
  border-bottom: none;
}

.modern-dropdown-item:hover {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.1), transparent);
  color: var(--primary-color);
}

.modern-dropdown-item:active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.2), transparent);
}

.item-icon {
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.online-users-btn {
  padding: 8px 16px;
  background: var(--bg-card);
  color: var(--text-white);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--transition);
  backdrop-filter: blur(10px);
}

.online-users-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.online-icon {
  font-size: 18px;
}

.dashboard-btn {
  padding: 8px 16px;
  background: var(--bg-card);
  color: var(--text-white);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--transition);
  backdrop-filter: blur(10px);
}

.dashboard-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.dashboard-icon {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 15px;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  color: var(--text-white);
  box-shadow: var(--shadow-sm);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-white);
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: var(--text-light);
  line-height: 1.2;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
  margin-top: 80px;
  margin-bottom: 80px; /* 添加底部边距，防止内容被页脚覆盖 */
  background: var(--bg-primary);
  min-height: calc(100vh - 160px); /* 减去顶部和底部的高度 */
  overflow-y: auto; /* 允许内容区域滚动 */
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
  z-index: 1000;
}

.modal {
  background: var(--bg-secondary);
  padding: 0;
  border-radius: var(--radius-lg);
  width: 500px;
  max-width: 90%;
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.modal.large-modal {
  width: 800px; /* Adjust as needed for large modal */
  max-width: 95%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: var(--primary-gradient);
  color: var(--text-white);
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-white);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-content {
  padding: 20px;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
}

.modal-content p {
  margin-bottom: 12px;
}

.modal-content strong {
  color: var(--primary-color);
  font-weight: 600;
}

.help-list {
  padding-left: 0;
  list-style: none;
  margin: 16px 0;
}

.help-list li {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--primary-color);
}

.help-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.logout-item {
  color: #ff6b6b !important;
}

.logout-item:hover {
  background: rgba(255, 107, 107, 0.1) !important;
  color: #ff6b6b !important;
}

.modal-footer {
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-primary {
  padding: 8px 16px;
  background: var(--primary-color);
  color: var(--text-white);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: var(--transition-fast);
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
</style> 