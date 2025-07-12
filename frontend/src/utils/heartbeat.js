import { authApi } from '../api/auth';

let heartbeatInterval = null;
const HEARTBEAT_INTERVAL = 60000; // 60秒

/**
 * 启动心跳检测
 * 定期向服务器发送心跳信号，维持用户在线状态
 */
export const startHeartbeat = () => {
  // 先停止之前的心跳检测（如果有）
  stopHeartbeat();
  
  // 立即发送一次心跳
  sendHeartbeat();
  
  // 设置定时发送
  heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
  
  // 添加页面可见性变化监听器
  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  // 添加页面卸载事件监听器
  window.addEventListener('beforeunload', stopHeartbeat);
};

/**
 * 停止心跳检测
 */
export const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
    
    // 移除事件监听器
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('beforeunload', stopHeartbeat);
  }
};

/**
 * 发送心跳
 */
const sendHeartbeat = async () => {
  // 检查token是否存在，优先使用sessionStorage，然后是localStorage
  const token = sessionStorage.getItem('token') || localStorage.getItem('token');
  if (!token) {
    console.warn('心跳检测: 未找到token，停止心跳');
    stopHeartbeat();
    return;
  }
  
  try {
    await authApi.heartbeat();
  } catch (error) {
    // 如果返回401错误，说明token无效，停止心跳
    if (error.response && error.response.status === 401) {
      console.warn('心跳检测: 收到401错误，停止心跳');
      stopHeartbeat();
    }
  }
};

/**
 * 处理页面可见性变化
 * 当页面重新变为可见时，立即发送心跳
 */
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    sendHeartbeat();
  }
}; 