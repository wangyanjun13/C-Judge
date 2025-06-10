import axios from '../utils/axios';

// 认证相关API
export const authApi = {
  // 登录
  login: (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    return axios.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  },
  
  // 注册（仅开发环境使用）
  register: (userData) => {
    return axios.post('/api/auth/register', userData);
  },
  
  // 修改密码
  changePassword: (oldPassword, newPassword) => {
    return axios.post('/api/auth/change-password', { old_password: oldPassword, new_password: newPassword });
  },
  
  // 登出
  logout: () => {
    return axios.post('/api/auth/logout-simple');
  },
  
  // 获取当前用户信息
  getCurrentUser: () => {
    return axios.get('/api/auth/me');
  }
};

export default authApi; 