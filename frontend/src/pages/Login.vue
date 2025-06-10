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
      
      <div class="api-test-section">
        <p>API连接状态: <span :class="apiStatus.class">{{ apiStatus.text }}</span></p>
        <button 
          class="test-button" 
          @click="testApiConnection" 
          :disabled="testingApi"
        >
          {{ testingApi ? '测试中...' : '测试API连接' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const testingApi = ref(false);
const apiStatus = ref({ class: '', text: '' });

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码';
    return;
  }
  
  error.value = '';
  loading.value = true;
  
  try {
    await authStore.login(username.value, password.value);
    
    // 根据用户角色跳转到不同页面
    const role = authStore.userRole;
    if (role === 'admin') {
      router.push('/admin/exercises');
    } else if (role === 'teacher') {
      router.push('/teacher/exercises');
    } else {
      router.push('/student/exercises');
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
};

const testApiConnection = async () => {
  testingApi.value = true;
  apiStatus.value = { class: 'testing', text: '测试中...' };
  
  try {
    const response = await fetch('/api/test');
    if (response.ok) {
      apiStatus.value = { class: 'success', text: '连接成功' };
    } else {
      apiStatus.value = { class: 'error', text: '连接失败' };
    }
  } catch (err) {
    apiStatus.value = { class: 'error', text: '无法连接到API' };
  } finally {
    testingApi.value = false;
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

.api-test-section {
  margin-top: 20px;
  text-align: center;
}

.test-button {
  padding: 10px 20px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.test-button:hover {
  background-color: #40a9ff;
}

.test-button:disabled {
  background-color: #bae7ff;
  cursor: not-allowed;
}
</style> 