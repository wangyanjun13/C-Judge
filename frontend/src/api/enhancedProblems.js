import { getAllProblemsData, getProblemCategories, getProblemsByCategory } from './problems';
import { getTagTypes, getTags, getBatchProblemTags } from './tags';
import dataCache from '../utils/dataCache';

/**
 * 增强的题库API服务
 * 提供缓存、去重、性能优化等功能
 */
class EnhancedProblemsAPI {
  constructor() {
    this.cache = dataCache;
    this.defaultCacheTTL = 5 * 60 * 1000; // 5分钟缓存
    this.longCacheTTL = 30 * 60 * 1000; // 30分钟缓存（用于相对稳定的数据）
  }

  /**
   * 获取所有题库数据（优化版本）
   * @param {Object} options - 选项
   * @param {Number} options.tagId - 按标签ID过滤
   * @param {Array} options.tagIds - 按多个标签ID过滤，取交集
   * @param {Number} options.tagTypeId - 按标签类型ID过滤
   * @param {Boolean} options.forceRefresh - 强制刷新缓存
   * @returns {Promise<Object>} - 包含所有数据的对象
   */
  async getAllData(options = {}) {
    const { forceRefresh = false, ...filterOptions } = options;
    
    if (forceRefresh) {
      // 强制刷新时清除相关缓存
      this.cache.invalidatePattern('all-problems-data:*');
    }

    return this.cache.smartGet(
      'all-problems-data',
      filterOptions,
      () => getAllProblemsData(filterOptions),
      this.defaultCacheTTL
    );
  }

  /**
   * 获取题库分类（带缓存）
   * @param {Boolean} forceRefresh - 强制刷新
   * @returns {Promise<Array>} - 分类列表
   */
  async getCategories(forceRefresh = false) {
    if (forceRefresh) {
      this.cache.invalidatePattern('categories:*');
    }

    return this.cache.smartGet(
      'categories',
      {},
      () => getProblemCategories(),
      this.longCacheTTL // 分类数据相对稳定，使用长期缓存
    );
  }

  /**
   * 获取标签类型和标签（带缓存）
   * @param {Boolean} forceRefresh - 强制刷新
   * @returns {Promise<Object>} - 包含标签类型和标签的对象
   */
  async getTagsData(forceRefresh = false) {
    if (forceRefresh) {
      this.cache.invalidatePattern('tags-data:*');
    }

    return this.cache.smartGet(
      'tags-data',
      {},
      async () => {
        const [tagTypes, tags] = await Promise.all([
          getTagTypes(),
          getTags()
        ]);
        return { tagTypes, tags };
      },
      this.defaultCacheTTL
    );
  }

  /**
   * 获取指定分类下的题目（带缓存，用于向后兼容）
   * @param {String} categoryPath - 分类路径
   * @param {Object} options - 过滤选项
   * @param {Boolean} forceRefresh - 强制刷新
   * @returns {Promise<Array>} - 题目列表
   */
  async getProblemsByCategory(categoryPath, options = {}, forceRefresh = false) {
    const { forceRefresh: optionForceRefresh, ...filterOptions } = options;
    const shouldForceRefresh = forceRefresh || optionForceRefresh;

    if (shouldForceRefresh) {
      this.cache.invalidatePattern(`problems-category:*${categoryPath}*`);
    }

    const cacheKey = { categoryPath, ...filterOptions };
    return this.cache.smartGet(
      'problems-category',
      cacheKey,
      () => getProblemsByCategory(categoryPath, filterOptions),
      this.defaultCacheTTL
    );
  }

  /**
   * 批量获取题目标签（带缓存和去重）
   * @param {Array<String>} problemPaths - 题目路径列表
   * @param {Boolean} forceRefresh - 强制刷新
   * @returns {Promise<Object>} - 标签映射对象
   */
  async getBatchProblemTags(problemPaths, forceRefresh = false) {
    if (!problemPaths || problemPaths.length === 0) {
      return {};
    }

    // 生成缓存键，对路径进行排序以确保一致性
    const sortedPaths = [...problemPaths].sort();
    const cacheKey = { paths: sortedPaths };

    if (forceRefresh) {
      this.cache.invalidatePattern('batch-problem-tags:*');
    }

    return this.cache.smartGet(
      'batch-problem-tags',
      cacheKey,
      () => getBatchProblemTags(problemPaths),
      this.defaultCacheTTL
    );
  }

  /**
   * 预加载数据
   * 在用户可能需要之前预先加载数据到缓存中
   * @param {Object} options - 预加载选项
   */
  async preloadData(options = {}) {
    console.log('开始预加载数据...');
    
    try {
      // 并行预加载基础数据
      const promises = [
        this.getCategories(),
        this.getTagsData()
      ];

      // 如果指定了预加载所有题目数据
      if (options.preloadAllProblems) {
        promises.push(this.getAllData());
      }

      await Promise.all(promises);
      console.log('数据预加载完成');
    } catch (error) {
      console.error('数据预加载失败:', error);
    }
  }

  /**
   * 智能过滤题目
   * 根据选中的标签高效过滤题目，优先使用缓存
   * @param {Object} selectedTagIds - 选中的标签ID映射
   * @param {Array} allProblems - 所有题目列表
   * @param {Object} problemTags - 题目标签映射
   * @returns {Array} - 过滤后的题目列表
   */
  filterProblemsByTags(selectedTagIds, allProblems, problemTags) {
    // 如果没有选中任何标签，返回所有题目
    const hasSelection = Object.values(selectedTagIds).some(tagId => tagId !== '');
    if (!hasSelection) {
      return allProblems;
    }

    // 获取所有选中的标签ID
    const selectedTags = Object.values(selectedTagIds).filter(tagId => tagId !== '');
    
    return allProblems.filter(problem => {
      const tags = problemTags[problem.data_path] || [];
      const tagIds = tags.map(tag => tag.id);
      
      // 检查是否包含所有选中的标签（交集）
      return selectedTags.every(selectedTagId => tagIds.includes(selectedTagId));
    });
  }

  /**
   * 清除缓存
   * @param {String} pattern - 清除模式，不提供则清除所有
   */
  clearCache(pattern = null) {
    if (pattern) {
      return this.cache.invalidatePattern(pattern);
    } else {
      this.cache.clear();
    }
  }

  /**
   * 获取缓存统计信息
   * @returns {Object} - 缓存统计
   */
  getCacheStats() {
    return this.cache.getStats();
  }

  /**
   * 处理数据更新后的缓存失效
   * @param {String} type - 更新类型 ('problem', 'tag', 'category')
   * @param {String} identifier - 标识符
   */
  invalidateAfterUpdate(type, identifier = '*') {
    console.log(`数据更新，失效缓存: ${type}:${identifier}`);
    
    switch (type) {
      case 'problem':
        this.cache.invalidatePattern('all-problems-data:*');
        this.cache.invalidatePattern('problems-category:*');
        this.cache.invalidatePattern('batch-problem-tags:*');
        break;
      case 'tag':
        this.cache.invalidatePattern('tags-data:*');
        this.cache.invalidatePattern('all-problems-data:*');
        this.cache.invalidatePattern('batch-problem-tags:*');
        break;
      case 'category':
        this.cache.invalidatePattern('categories:*');
        this.cache.invalidatePattern('all-problems-data:*');
        break;
      default:
        this.cache.clear(); // 未知类型，清除所有缓存
    }
  }
}

// 创建全局实例
const enhancedProblemsAPI = new EnhancedProblemsAPI();

// 导出API实例和类
export default enhancedProblemsAPI;
export { EnhancedProblemsAPI }; 