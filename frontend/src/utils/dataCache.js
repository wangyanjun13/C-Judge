/**
 * 数据缓存管理器
 * 用于缓存题库、标签等数据，减少重复的API请求
 */
class DataCache {
  constructor() {
    this.cache = new Map();
    this.loadingPromises = new Map(); // 防止重复请求
    this.defaultTTL = 5 * 60 * 1000; // 默认缓存5分钟
  }

  /**
   * 生成缓存键
   * @param {string} type - 缓存类型
   * @param {Object} params - 参数对象
   * @returns {string} - 缓存键
   */
  generateKey(type, params = {}) {
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((result, key) => {
        result[key] = params[key];
        return result;
      }, {});
    
    return `${type}:${JSON.stringify(sortedParams)}`;
  }

  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {any} data - 要缓存的数据
   * @param {number} ttl - 生存时间（毫秒）
   */
  set(key, data, ttl = this.defaultTTL) {
    const expireTime = Date.now() + ttl;
    this.cache.set(key, {
      data,
      expireTime,
      createTime: Date.now()
    });
    
    console.log(`缓存设置: ${key}, TTL: ${ttl}ms`);
  }

  /**
   * 获取缓存
   * @param {string} key - 缓存键
   * @returns {any|null} - 缓存的数据或null
   */
  get(key) {
    const cached = this.cache.get(key);
    
    if (!cached) {
      return null;
    }
    
    // 检查是否过期
    if (Date.now() > cached.expireTime) {
      this.cache.delete(key);
      console.log(`缓存过期并删除: ${key}`);
      return null;
    }
    
    const age = Date.now() - cached.createTime;
    console.log(`缓存命中: ${key}, 年龄: ${age}ms`);
    return cached.data;
  }

  /**
   * 删除特定缓存
   * @param {string} key - 缓存键
   */
  delete(key) {
    const deleted = this.cache.delete(key);
    if (deleted) {
      console.log(`缓存删除: ${key}`);
    }
    return deleted;
  }

  /**
   * 清除所有缓存
   */
  clear() {
    const size = this.cache.size;
    this.cache.clear();
    this.loadingPromises.clear();
    console.log(`清除所有缓存, 清除了 ${size} 项`);
  }

  /**
   * 清除过期缓存
   */
  clearExpired() {
    const now = Date.now();
    let clearedCount = 0;
    
    for (const [key, cached] of this.cache.entries()) {
      if (now > cached.expireTime) {
        this.cache.delete(key);
        clearedCount++;
      }
    }
    
    if (clearedCount > 0) {
      console.log(`清除过期缓存: ${clearedCount} 项`);
    }
    
    return clearedCount;
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    this.clearExpired(); // 先清除过期缓存
    
    const stats = {
      totalItems: this.cache.size,
      items: []
    };
    
    for (const [key, cached] of this.cache.entries()) {
      const age = Date.now() - cached.createTime;
      const remaining = cached.expireTime - Date.now();
      
      stats.items.push({
        key,
        age,
        remaining,
        expired: remaining <= 0
      });
    }
    
    return stats;
  }

  /**
   * 防止重复请求的包装器
   * @param {string} key - 请求键
   * @param {Function} requestFn - 请求函数
   * @returns {Promise} - 请求Promise
   */
  async withDeduplication(key, requestFn) {
    // 检查是否已有相同的请求在进行中
    if (this.loadingPromises.has(key)) {
      console.log(`请求去重: ${key}`);
      return this.loadingPromises.get(key);
    }
    
    // 执行请求
    const promise = requestFn().finally(() => {
      // 请求完成后清除loading状态
      this.loadingPromises.delete(key);
    });
    
    this.loadingPromises.set(key, promise);
    return promise;
  }

  /**
   * 智能获取数据（优先从缓存，缓存不存在则请求）
   * @param {string} type - 数据类型
   * @param {Object} params - 请求参数
   * @param {Function} requestFn - 请求函数
   * @param {number} ttl - 缓存时间
   * @returns {Promise} - 数据
   */
  async smartGet(type, params, requestFn, ttl = this.defaultTTL) {
    const key = this.generateKey(type, params);
    
    // 先尝试从缓存获取
    const cached = this.get(key);
    if (cached) {
      return cached;
    }
    
    // 缓存不存在，发起请求（带去重）
    const data = await this.withDeduplication(key, requestFn);
    
    // 缓存结果
    this.set(key, data, ttl);
    
    return data;
  }

  /**
   * 失效相关缓存
   * @param {string} pattern - 匹配模式（支持简单的通配符）
   */
  invalidatePattern(pattern) {
    let clearedCount = 0;
    const regex = new RegExp(pattern.replace(/\*/g, '.*'));
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
        clearedCount++;
      }
    }
    
    console.log(`模式失效缓存: ${pattern}, 清除了 ${clearedCount} 项`);
    return clearedCount;
  }
}

// 创建全局缓存实例
const dataCache = new DataCache();

// 定期清理过期缓存
setInterval(() => {
  dataCache.clearExpired();
}, 60 * 1000); // 每分钟清理一次

export default dataCache; 