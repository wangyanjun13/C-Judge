<template>
  <div class="login-container">
    <div class="login-box">
      <h1>C语言评测系统</h1>
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="请输入用户名"
          @keyup.enter="handleLogin"
        >
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="请输入密码"
          @keyup.enter="handleLogin"
        >
      </div>
      <div class="error-message" v-if="error">{{ error }}</div>
      <button 
        class="login-button" 
        @click="handleLogin" 
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <div class="login-options">
        <button class="text-button" @click="clearStorage">清除登录状态</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { ElMessage } from 'element-plus';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

// 在页面加载时简单检查token
onMounted(() => {
  try {
    // 清除可能存在的错误信息
    error.value = '';
    
    // 如果已经登录，直接跳转
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user && user.role) {
          redirectToUserPage(user.role);
        }
      } catch (e) {
        console.error('解析用户数据出错:', e);
        clearStorage();
      }
    }
  } catch (err) {
    console.error('初始化登录页时出错:', err);
  }
});

// 清除存储数据
const clearStorage = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    ElMessage.success('登录状态已清除');
  } catch (err) {
    console.error('清除存储数据时出错:', err);
  }
};

// 根据角色跳转到对应页面
const redirectToUserPage = (role) => {
  if (role === 'admin') {
    router.push('/admin/exercises');
  } else if (role === 'teacher') {
    router.push('/teacher/exercises');
  } else if (role === 'student') {
    router.push('/student/exercises');
  }
};

// 处理登录
const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码';
    return;
  }
  
  error.value = '';
  loading.value = true;
  
  try {
    const result = await authStore.login(username.value, password.value);
    console.log('登录成功:', result);
    
    // 根据用户角色跳转
    const role = authStore.userRole;
    if (role) {
      redirectToUserPage(role);
    } else {
      error.value = '登录成功但无法确定用户角色';
    }
  } catch (err) {
    console.error('登录失败:', err);
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.error-message {
  color: #ff4d4f;
  margin-bottom: 15px;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #40a9ff;
}

.login-button:disabled {
  background-color: #bae7ff;
  cursor: not-allowed;
}

.login-options {
  margin-top: 20px;
  text-align: center;
}

.text-button {
  background: none;
  border: none;
  color: #1890ff;
  text-decoration: underline;
  cursor: pointer;
  font-size: 14px;
}

.text-button:hover {
  color: #40a9ff;
}
</style> 