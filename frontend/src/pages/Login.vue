<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Just For Fun</h1>
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
      <p>© {{ currentYear }}  Just For Fun - 编程评测系统</p>
      <p class="license-text">
        <span class="license-link" @click="showLicense">MIT License -  MIT 许可证</span>
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
    
    // 如果已经登录，直接跳转 - 优先使用sessionStorage
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        // 确保数据存储在sessionStorage中，以防是从localStorage读取的
        if (!sessionStorage.getItem('token') && localStorage.getItem('token')) {
          sessionStorage.setItem('token', token);
          sessionStorage.setItem('user', userStr);
          // 清除localStorage中的数据，防止跨标签页干扰
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
        
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
    // 同时清除sessionStorage和localStorage
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
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
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background-color: #f5f5f5;
  background-image: url('/justforfun_new.png');
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
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
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 2;
  margin: 0 0 0 830px;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.login-box:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  transform: translateY(-15px);
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #667eea;
  font-weight: 700;
  font-size: 28px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
}

.form-group {
  margin-bottom: 24px;
  position: relative;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
  transition: all 0.3s ease;
}

input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.error-message {
  color: #ff4d4f;
  margin: -10px 0 15px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.login-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
  box-shadow: 0 3px 8px rgba(102, 126, 234, 0.3);
}

.login-button:disabled {
  background: linear-gradient(135deg, #a9b4f5 0%, #b79ed1 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-options {
  margin-top: 24px;
  text-align: center;
}

.text-button {
  background: none;
  border: none;
  color: #667eea;
  text-decoration: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  padding: 5px 10px;
  border-radius: 4px;
}

.text-button:hover {
  color: #764ba2;
  background-color: rgba(102, 126, 234, 0.1);
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
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0) 100%);
}

.login-footer p {
  margin: 5px 0;
}

.license-text {
  font-size: 12px;
  opacity: 0.8;
  transition: all 0.2s ease;
}

.license-link {
  cursor: pointer;
  text-decoration: underline;
  transition: all 0.2s ease;
  padding: 2px 5px;
  border-radius: 3px;
}

.license-link:hover {
  color: #fff;
  opacity: 1;
  background-color: rgba(255, 255, 255, 0.1);
}

/* 响应式调整 */
@media (max-height: 700px) {
  .login-box {
    margin: 0 0 0 100px;
    padding: 30px;
    transform: translateY(30px);
  }
  
  .login-footer {
    position: relative;
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .login-box {
    margin: 0 0 0 80px;
    transform: translateY(40px);
  }
}

@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
    margin: 0 0 0 30px;
    transform: translateY(30px);
  }
}

.license-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.license-modal {
  background-color: white;
  padding: 25px;
  border-radius: 16px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  color: #333;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: modal-in 0.3s ease;
}

@keyframes modal-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.license-modal h3 {
  margin-top: 0;
  color: #667eea;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
  font-size: 22px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.license-content {
  margin: 20px 0;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  color: #444;
}

.license-modal button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  float: right;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
}

.license-modal button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}
</style> 