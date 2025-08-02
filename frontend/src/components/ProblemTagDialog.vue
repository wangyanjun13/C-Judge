<template>
  <div class="problem-tag-dialog">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else class="dialog-content">
      <!-- 左侧：题目内容 -->
      <div class="problem-content">
        <h3>{{ problem.chinese_name || problem.name }}</h3>
        <div class="problem-html" v-html="problem.html_content"></div>
      </div>
      
      <!-- 右侧：标签选择 -->
      <div class="tags-section">
        <h4>设置标签</h4>
        <div class="tag-selection">
          <div v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-section">
            <h5>{{ tagType.name }}</h5>
            <div class="tag-list">
              <div 
                v-for="tag in getTagsByType(tagType.id)" 
                :key="tag.id" 
                class="tag-item"
                :class="{ selected: selectedTags.includes(tag.id) }"
                @click="toggleTag(tag.id)"
              >
                {{ tag.name }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-actions">
          <button @click="$emit('cancel')" class="btn btn-cancel">取消</button>
          <button @click="saveTags" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getProblemDetail } from '../api/exercises';
import { getTagTypes, getTags, getProblemTags, setProblemTags } from '../api/tags';

const props = defineProps({
  problemInfo: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['cancel', 'saved']);

const problem = ref({});
const loading = ref(true);
const error = ref(null);
const tagTypes = ref([]);
const allTags = ref([]);
const selectedTags = ref([]);

// 根据标签类型获取标签
const getTagsByType = (tagTypeId) => {
  return allTags.value.filter(tag => tag.tag_type_id === tagTypeId);
};

// 切换标签选择状态
const toggleTag = (tagId) => {
  const index = selectedTags.value.indexOf(tagId);
  if (index === -1) {
    selectedTags.value.push(tagId);
  } else {
    selectedTags.value.splice(index, 1);
  }
};

// 保存标签
const saveTags = async () => {
  try {
    const problemPath = encodeURIComponent(props.problemInfo.data_path);
    await setProblemTags(problemPath, selectedTags.value);
    ElMessage.success('标签设置成功');
    emit('saved', selectedTags.value);
  } catch (error) {
    console.error('设置问题标签失败:', error);
    ElMessage.error('设置问题标签失败');
  }
};

// 加载数据
const loadData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 加载标签类型和标签
    const [tagTypesData, tagsData] = await Promise.all([
      getTagTypes(),
      getTags()
    ]);
    
    tagTypes.value = tagTypesData;
    allTags.value = tagsData;
    
    // 根据data_path构建题目详情
    if (props.problemInfo.data_path) {
      // 从题库路径生成HTML内容的API调用
      try {
        const response = await fetch(`/api/problems/html/${encodeURIComponent(props.problemInfo.data_path)}`);
        if (response.ok) {
          const htmlContent = await response.text();
          problem.value = {
            ...props.problemInfo,
            html_content: htmlContent
          };
        } else {
          // 如果获取HTML失败，至少显示基本信息
          problem.value = {
            ...props.problemInfo,
            html_content: `<h3>${props.problemInfo.chinese_name || props.problemInfo.name}</h3><p>题目详情加载失败</p>`
          };
        }
      } catch (err) {
        console.error('获取题目HTML内容失败:', err);
        problem.value = {
          ...props.problemInfo,
          html_content: `<h3>${props.problemInfo.chinese_name || props.problemInfo.name}</h3><p>题目详情加载失败</p>`
        };
      }
      
      // 获取已有标签
      try {
        const problemPath = encodeURIComponent(props.problemInfo.data_path);
        const existingTags = await getProblemTags(problemPath);
        selectedTags.value = existingTags.map(tag => tag.id);
      } catch (err) {
        console.error('获取已有标签失败:', err);
        selectedTags.value = [];
      }
    }
  } catch (err) {
    console.error('加载数据失败:', err);
    error.value = '加载数据失败';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.problem-tag-dialog {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 700px;
}

.loading, .error {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.dialog-content {
  display: flex;
  height: calc(100vh - 180px);
  min-height: 650px;
  gap: 20px;
  overflow: hidden;
}

.problem-content {
  flex: 2;
  overflow-y: auto;
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border: none;
  min-width: 60%;
  max-height: 100%;
}

.problem-content h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.problem-html {
  line-height: 1.6;
  color: #303133;
  overflow-wrap: break-word;
}

.problem-html :deep(p) {
  margin: 1em 0;
}

.problem-html :deep(pre) {
  background-color: #f8f8f9;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.tags-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ebeef5;
  padding-left: 20px;
  min-width: 300px;
  max-width: 400px;
}

.tags-section h4 {
  margin-top: 0;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  flex-shrink: 0;
}

.tag-selection {
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 280px);
  padding-right: 5px;
}

.tag-type-section {
  margin-bottom: 20px;
}

.tag-type-section h5 {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 12px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
  border: 1px solid #dcdfe6;
}

.tag-item:hover {
  background-color: #e9e9eb;
}

.tag-item.selected {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.dialog-actions {
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-cancel {
  background-color: #909399;
  color: white;
}

.btn-cancel:hover {
  background-color: #a6a9ad;
}
</style> 