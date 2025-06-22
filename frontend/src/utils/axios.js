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
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 输出请求详情到控制台（仅开发环境）
    if (import.meta.env.DEV) {
      console.log('API请求:', {
        url: config.url,
        method: config.method,
        headers: config.headers,
        data: config.data
      })
    }
    
    return config
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
    // 如果是操作日志相关的请求，静默处理错误
    if (error.config && error.config.url && error.config.url.includes('/api/operation-logs')) {
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
          message = '未授权'
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