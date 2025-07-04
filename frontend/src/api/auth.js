import axios from '../utils/axios';

// 认证相关API
export const authApi = {
  // 登录
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return axios.post('/api/auth/login', formData);
  },
  
  // 注册
  register: (userData) => {
    return axios.post('/api/auth/register', userData);
  },
  
  // 修改密码
  changePassword: (oldPassword, newPassword) => {
    return axios.post('/api/auth/change-password', { old_password: oldPassword, new_password: newPassword });
  },
  
  // 登出
  logout: () => {
    return axios.post('/api/auth/logout');
  },
  
  // 简单登出（不需要验证）
  logoutSimple: () => {
    return axios.post('/api/auth/logout-simple');
  },
  
  // 获取当前用户信息
  getCurrentUser: () => {
    return axios.get('/api/auth/me');
  },
  
  // 获取在线用户
  getOnlineUsers: () => {
    return axios.get('/api/auth/online-users')
      .then(response => {
        return {
          data: response.data,
          status: response.status
        };
      })
      .catch(error => {
        console.warn('获取在线用户列表失败:', error);
        throw error;
      });
  },
  
  // 心跳检测
  heartbeat: () => {
    return axios.post('/api/auth/heartbeat');
  }
};

export default authApi; 