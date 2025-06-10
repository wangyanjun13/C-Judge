import { defineStore } from 'pinia';
import { authApi } from '../api/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  
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
        this.setAuth(response);
        return response;
      } catch (error) {
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
        this.setAuth(response);
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
          const user = await authApi.getCurrentUser();
          this.user = user;
          return true;
        } catch (error) {
          this.clearAuth();
          return false;
        }
      }
      return false;
    },
    
    // 设置认证信息
    setAuth(data) {
      this.token = data.access_token;
      this.user = data.user;
      
      // 保存到本地存储
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    },
    
    // 清除认证信息
    clearAuth() {
      this.user = null;
      this.token = null;
      
      // 从本地存储中移除
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
});