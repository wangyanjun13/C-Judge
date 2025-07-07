import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const instance = axios.create({
  baseURL: '',  // 确保为空，使用相对路径
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true  // 确保跨域请求携带凭证
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 当Content-Type为multipart/form-data时，不要设置Content-Type，让浏览器自动设置
    if (config.data instanceof FormData) {
      // 使用FormData时，删除Content-Type让浏览器自动设置boundary
      delete config.headers['Content-Type'];
    }
    
    console.log('API请求: ', config);
    
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    
    // 如果token存在，添加到请求头中
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 下面这些请求出错时不显示全局提示
    const silentPaths = [
      '/api/auth/heartbeat',
      '/api/auth/online-users',
      '/api/operation-logs'
    ];
    
    // 检查当前请求是否应该静默处理
    const shouldBeSilent = silentPaths.some(path => 
      error.config && error.config.url && error.config.url.includes(path)
    );
    
    if (shouldBeSilent) {
      return Promise.reject(error);
    }
    
    let message = '未知错误'
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.detail || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 如果是401错误，可能是token过期，清除本地token
          if (!error.config.url.includes('/api/auth/login')) {
            localStorage.removeItem('token');
          }
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器错误'
          break
        default:
          message = `请求错误 (${status})`
      }
    } else if (error.request) {
      message = '服务器无响应'
    } else {
      message = error.message
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default instance 