/**
 * localStorage 工具函数，提供安全的本地存储操作
 */

/**
 * 安全地从 localStorage 获取数据并解析 JSON
 * @param {string} key - 存储键名
 * @param {any} defaultValue - 当键不存在或解析失败时返回的默认值
 * @returns {any} 解析后的数据或默认值
 */
export const getItem = (key, defaultValue = null) => {
  try {
    const value = localStorage.getItem(key);
    if (value === null || value === undefined) {
      return defaultValue;
    }
    return JSON.parse(value);
  } catch (error) {
    console.error(`从localStorage获取 ${key} 时出错:`, error);
    return defaultValue;
  }
};

/**
 * 安全地将数据保存到 localStorage
 * @param {string} key - 存储键名
 * @param {any} value - 要存储的数据（将被 JSON 序列化）
 * @returns {boolean} 操作是否成功
 */
export const setItem = (key, value) => {
  try {
    if (value === undefined) {
      console.warn(`尝试将 undefined 值存储到 ${key} 键中，已改为存储 null`);
      value = null;
    }
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`保存数据到localStorage的 ${key} 键时出错:`, error);
    return false;
  }
};

/**
 * 从 localStorage 中移除指定键
 * @param {string} key - 要移除的键名
 * @returns {boolean} 操作是否成功
 */
export const removeItem = (key) => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`从localStorage移除 ${key} 时出错:`, error);
    return false;
  }
};

/**
 * 清除所有 localStorage 数据
 * @returns {boolean} 操作是否成功
 */
export const clear = () => {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.error('清除localStorage时出错:', error);
    return false;
  }
};

/**
 * 检查 localStorage 中是否存在指定键
 * @param {string} key - 要检查的键名
 * @returns {boolean} 键是否存在
 */
export const hasKey = (key) => {
  return localStorage.getItem(key) !== null;
};

/**
 * 修复 localStorage 中可能损坏的数据
 * 检查常用键并尝试修复无效 JSON
 * @returns {Object} 包含修复状态的对象
 */
export const fixCorruptedStorage = () => {
  const keysToCheck = ['user', 'token', 'settings'];
  const fixed = {};
  
  keysToCheck.forEach(key => {
    try {
      const value = localStorage.getItem(key);
      if (value) {
        // 尝试解析 JSON，如果失败则移除该键
        try {
          JSON.parse(value);
          fixed[key] = false; // 不需要修复
        } catch (e) {
          localStorage.removeItem(key);
          fixed[key] = true; // 已修复（移除）
        }
      }
    } catch (error) {
      console.error(`检查 ${key} 时出错:`, error);
    }
  });
  
  return { fixed, keysChecked: keysToCheck };
};

export default {
  getItem,
  setItem,
  removeItem,
  clear,
  hasKey,
  fixCorruptedStorage
}; 