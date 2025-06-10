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
    // 输出响应详情到控制台（仅开发环境）
    if (import.meta.env.DEV) {
      console.log('API响应:', {
        url: response.config.url,
        status: response.status,
        data: response.data
      })
    }
    
    return response
  },
  error => {
    let message = '未知错误'
    
    // 输出错误详情到控制台（仅开发环境）
    if (import.meta.env.DEV) {
      console.error('API错误:', {
        url: error.config?.url,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        code: error.code
      })
    }
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.detail || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 清除token
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          // 如果不是登录页，重定向到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
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
      // 请求已发送但未收到响应
      message = '服务器无响应，请检查网络连接'
    } else {
      // 请求过程中发生错误
      message = error.message
    }
    
    // 显示错误消息
    ElMessage.error(message)
    console.error('响应错误:', error)
    
    return Promise.reject(error)
  }
)

export default instance 