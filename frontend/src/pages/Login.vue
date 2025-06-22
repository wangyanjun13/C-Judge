<template>
  <div class="login-container">
    <div class="login-box">
      <h1>C-Judge测评系统</h1>
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
    
    <div class="login-footer">
      <p>© {{ currentYear }} 王彦军 & 北京语言大学 C-Judge 测评系统</p>
      <p class="license-text">
        <span class="license-link" @click="showLicense">MIT License - 根据 MIT 许可证</span>
      </p>
    </div>
    
    <!-- LICENSE 弹窗 -->
    <div v-if="licenseVisible" class="license-modal-overlay" @click="licenseVisible = false">
      <div class="license-modal" @click.stop>
        <h3>MIT License</h3>
        <div class="license-content">
          <p>Copyright (c) {{ currentYear }} wangyanjun13</p>
          <p>
            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:
          </p>
          <p>
            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.
          </p>
          <p>
            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.
          </p>
        </div>
        <button @click="licenseVisible = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { ElMessage } from 'element-plus';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

// 计算当前年份，用于版权信息
const currentYear = computed(() => new Date().getFullYear());

// LICENSE 弹窗控制
const licenseVisible = ref(false);
const showLicense = () => {
  licenseVisible.value = true;
};

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
  flex-direction: column;
  justify-content: center;  /* 改回居中对齐 */
  align-items: center;      /* 改回居中对齐 */
  min-height: 100vh;
  width: 100%;
  background-color: #f5f5f5;
  background-image: url('/background.svg');
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden; /* 防止内容溢出 */
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.login-box {
  width: 400px;
  max-width: 90%;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 2;
  margin: 0 0 0 830px;  /* 从中间位置向右偏移 */
  transform: translateY(-10px);  /* 从中间位置向上偏移 */
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

.login-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  color: white;
  font-size: 14px;
  z-index: 2;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  padding: 15px 0;
}

.login-footer p {
  margin: 5px 0;
}

.license-text {
  font-size: 12px;
  opacity: 0.8;
}

.license-link {
  cursor: pointer;
  text-decoration: underline;
}

.license-link:hover {
  color: #fff;
  opacity: 1;
}

/* 响应式调整 */
@media (max-height: 700px) {
  .login-box {
    margin: 0 0 0 100px;  /* 小屏幕上减少偏移量 */
    padding: 30px;
    transform: translateY(30px);  /* 小屏幕上减少向下偏移 */
  }
  
  .login-footer {
    position: relative;
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .login-box {
    margin: 0 0 0 80px;  /* 平板上减少偏移量 */
    transform: translateY(40px);
  }
}

@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
    margin: 0 0 0 30px;  /* 手机上进一步减少偏移量 */
    transform: translateY(30px);
  }
}

.license-modal-overlay {
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

.license-modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.license-modal h3 {
  margin-top: 0;
  color: #1890ff;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.license-content {
  margin: 20px 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.license-modal button {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  float: right;
}

.license-modal button:hover {
  background-color: #40a9ff;
}
</style> 