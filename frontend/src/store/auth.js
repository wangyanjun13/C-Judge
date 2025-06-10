import { defineStore } from 'pinia';
import { authApi } from '../api/auth';
import storage from '../utils/localStorage';

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      user: null,
      token: null,
      loading: false,
      error: null
    };
  },
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user && state.user.role === 'admin',
    isTeacher: (state) => state.user && state.user.role === 'teacher',
    isStudent: (state) => state.user && state.user.role === 'student',
    userRole: (state) => state.user ? state.user.role : null
  },
  
  actions: {
    // 登录
    async login(username, password) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await authApi.login(username, password);
        console.log('登录响应:', response.data);
        if (response && response.data) {
          this.setAuth(response.data);
          return response.data;
        } else {
          throw new Error('登录响应无效');
        }
      } catch (error) {
        console.error('登录错误:', error);
        this.error = error.response?.data?.detail || '登录失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // 注册
    async register(userData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await authApi.register(userData);
        if (response && response.data) {
          this.setAuth(response.data);
          return response.data;
        }
        return response;
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // 修改密码
    async changePassword(oldPassword, newPassword) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await authApi.changePassword(oldPassword, newPassword);
        return response;
      } catch (error) {
        this.error = error.response?.data?.detail || '修改密码失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // 登出
    async logout() {
      this.loading = true;
      
      try {
        await authApi.logout();
      } catch (error) {
        console.error('登出错误', error);
      } finally {
        this.clearAuth();
        this.loading = false;
      }
    },
    
    // 恢复会话
    async restoreSession() {
      if (this.token) {
        try {
          const response = await authApi.getCurrentUser();
          if (response && response.data) {
            this.user = response.data;
            return true;
          }
          return false;
        } catch (error) {
          console.error('恢复会话错误:', error);
          this.clearAuth();
          return false;
        }
      }
      return false;
    },
    
    // 设置认证信息
    setAuth(data) {
      console.log('设置认证信息:', data);
      
      // 从响应中安全获取字段
      let token = null;
      let user = null;
      
      // 检查不同可能的字段名
      if (data.access_token) {
        token = data.access_token;
      } else if (data.token) {
        token = data.token;
      }
      
      // 获取用户信息
      if (data.user) {
        user = data.user;
      }
      
      // 更新状态
      this.token = token;
      this.user = user;
      
      // 保存到本地存储
      if (token) {
        localStorage.setItem('token', token);
      }
      
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      }
    },
    
    // 清除认证信息
    clearAuth() {
      this.user = null;
      this.token = null;
      
      // 从本地存储中移除
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
    
    // 修复存储数据
    fixStorage() {
      return storage.fixCorruptedStorage();
    }
  }
});