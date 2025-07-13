<template>
  <div class="tag-manager">
    <div class="tag-manager-header">
      <h3>标签管理</h3>
      <button @click="closeDialog" class="close-btn">&times;</button>
    </div>
    
    <div class="tag-manager-content">
      <div class="tag-types-section">
        <div class="section-header">
          <h4>标签类型</h4>
          <button @click="showAddTagTypeForm" class="btn btn-primary">添加类型</button>
        </div>
        
        <div v-if="addingTagType" class="add-form">
          <input v-model="newTagType.name" placeholder="标签类型名称" />
          <div class="form-actions">
            <button @click="cancelAddTagType" class="btn">取消</button>
            <button @click="addTagType" class="btn btn-primary">确定</button>
          </div>
        </div>
        
        <div class="tag-types-list">
          <div 
            v-for="tagType in tagTypes" 
            :key="tagType.id" 
            class="tag-type-item"
            :class="{ active: selectedTagType && selectedTagType.id === tagType.id }"
            @click="selectTagType(tagType)"
          >
            <span>{{ tagType.name }}</span>
            <div class="tag-type-actions">
              <button @click.stop="editTagType(tagType)" class="btn-icon">✏️</button>
              <button @click.stop="confirmDeleteTagType(tagType)" class="btn-icon">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="tags-section" v-if="selectedTagType">
        <div class="section-header">
          <h4>{{ selectedTagType.name }}标签</h4>
          <button @click="showAddTagForm" class="btn btn-primary">添加标签</button>
        </div>
        
        <div v-if="addingTag" class="add-form">
          <input v-model="newTag.name" placeholder="标签名称" />
          <div class="form-actions">
            <button @click="cancelAddTag" class="btn">取消</button>
            <button @click="addTag" class="btn btn-primary">确定</button>
          </div>
        </div>
        
        <div class="tags-list">
          <div v-for="tag in filteredTags" :key="tag.id" class="tag-item">
            <span>{{ tag.name }}</span>
            <div class="tag-actions">
              <button @click="editTag(tag)" class="btn-icon">✏️</button>
              <button @click="confirmDeleteTag(tag)" class="btn-icon">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑标签类型对话框 -->
    <div v-if="editingTagType" class="modal-overlay">
      <div class="modal">
        <h3>编辑标签类型</h3>
        <input v-model="editTagTypeForm.name" placeholder="标签类型名称" />
        <div class="form-actions">
          <button @click="cancelEditTagType" class="btn">取消</button>
          <button @click="updateTagType" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 编辑标签对话框 -->
    <div v-if="editingTag" class="modal-overlay">
      <div class="modal">
        <h3>编辑标签</h3>
        <input v-model="editTagForm.name" placeholder="标签名称" />
        <div class="form-actions">
          <button @click="cancelEditTag" class="btn">取消</button>
          <button @click="updateTag" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 确认删除对话框 -->
    <div v-if="showConfirmDelete" class="modal-overlay">
      <div class="modal">
        <h3>确认删除</h3>
        <p>{{ confirmDeleteMessage }}</p>
        <div class="form-actions">
          <button @click="cancelDelete" class="btn">取消</button>
          <button @click="confirmDelete" class="btn btn-danger">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { 
  getTagTypes, createTagType, updateTagType as updateTagTypeAPI, deleteTagType as deleteTagTypeAPI,
  getTags, createTag, updateTag as updateTagAPI, deleteTag as deleteTagAPI
} from '../api/tags';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'update']);

// 标签类型相关状态
const tagTypes = ref([]);
const selectedTagType = ref(null);
const addingTagType = ref(false);
const newTagType = ref({ name: '' });
const editingTagType = ref(false);
const editTagTypeForm = ref({ id: null, name: '' });

// 标签相关状态
const tags = ref([]);
const addingTag = ref(false);
const newTag = ref({ name: '', tag_type_id: null });
const editingTag = ref(false);
const editTagForm = ref({ id: null, name: '', tag_type_id: null });

// 删除确认相关状态
const showConfirmDelete = ref(false);
const confirmDeleteMessage = ref('');
const deleteCallback = ref(null);

// 计算属性：根据选中的标签类型过滤标签
const filteredTags = computed(() => {
  if (!selectedTagType.value) return [];
  return tags.value.filter(tag => tag.tag_type_id === selectedTagType.value.id);
});

// 生命周期钩子
onMounted(async () => {
  await loadTagTypes();
});

// 加载标签类型
const loadTagTypes = async () => {
  try {
    tagTypes.value = await getTagTypes();
    if (tagTypes.value.length > 0 && !selectedTagType.value) {
      selectTagType(tagTypes.value[0]);
    }
  } catch (error) {
    console.error('加载标签类型失败:', error);
    ElMessage.error('加载标签类型失败');
  }
};

// 加载标签
const loadTags = async () => {
  try {
    if (selectedTagType.value) {
      // 如果选中了标签类型，则只加载该类型的标签
      tags.value = await getTags(selectedTagType.value.id);
    } else {
      // 否则加载所有标签
    tags.value = await getTags();
    }
  } catch (error) {
    console.error('加载标签失败:', error);
    ElMessage.error('加载标签失败');
  }
};

// 选择标签类型
const selectTagType = async (tagType) => {
  selectedTagType.value = tagType;
  await loadTags();
};

// 显示添加标签类型表单
const showAddTagTypeForm = () => {
  addingTagType.value = true;
  newTagType.value = { name: '' };
};

// 取消添加标签类型
const cancelAddTagType = () => {
  addingTagType.value = false;
};

// 添加标签类型
const addTagType = async () => {
  if (!newTagType.value.name) {
    ElMessage.warning('请输入标签类型名称');
    return;
  }
  
  try {
    const createdTagType = await createTagType(newTagType.value);
    tagTypes.value.push(createdTagType);
    addingTagType.value = false;
    ElMessage.success('添加标签类型成功');
    emit('update');
  } catch (error) {
    console.error('添加标签类型失败:', error);
    ElMessage.error('添加标签类型失败');
  }
};

// 编辑标签类型
const editTagType = (tagType) => {
  editTagTypeForm.value = { ...tagType };
  editingTagType.value = true;
};

// 取消编辑标签类型
const cancelEditTagType = () => {
  editingTagType.value = false;
};

// 更新标签类型
const updateTagType = async () => {
  if (!editTagTypeForm.value.name) {
    ElMessage.warning('请输入标签类型名称');
    return;
  }
  
  try {
    const updatedTagType = await updateTagTypeAPI(editTagTypeForm.value.id, { name: editTagTypeForm.value.name });
    const index = tagTypes.value.findIndex(t => t.id === updatedTagType.id);
    if (index !== -1) {
      tagTypes.value[index] = updatedTagType;
    }
    editingTagType.value = false;
    ElMessage.success('更新标签类型成功');
    emit('update');
  } catch (error) {
    console.error('更新标签类型失败:', error);
    ElMessage.error('更新标签类型失败');
  }
};

// 确认删除标签类型
const confirmDeleteTagType = (tagType) => {
  confirmDeleteMessage.value = `确定要删除标签类型 "${tagType.name}" 吗？这将同时删除该类型下的所有标签。`;
  deleteCallback.value = () => deleteTagType(tagType);
  showConfirmDelete.value = true;
};

// 删除标签类型
const deleteTagType = async (tagType) => {
  try {
    await deleteTagTypeAPI(tagType.id);
    tagTypes.value = tagTypes.value.filter(t => t.id !== tagType.id);
    if (selectedTagType.value && selectedTagType.value.id === tagType.id) {
      selectedTagType.value = tagTypes.value.length > 0 ? tagTypes.value[0] : null;
    }
    ElMessage.success('删除标签类型成功');
    emit('update');
  } catch (error) {
    console.error('删除标签类型失败:', error);
    ElMessage.error('删除标签类型失败');
  }
};

// 显示添加标签表单
const showAddTagForm = () => {
  if (!selectedTagType.value) {
    ElMessage.warning('请先选择一个标签类型');
    return;
  }
  
  addingTag.value = true;
  newTag.value = { name: '', tag_type_id: selectedTagType.value.id };
};

// 取消添加标签
const cancelAddTag = () => {
  addingTag.value = false;
};

// 添加标签
const addTag = async () => {
  if (!newTag.value.name) {
    ElMessage.warning('请输入标签名称');
    return;
  }
  
  try {
    const createdTag = await createTag(newTag.value);
    tags.value.push(createdTag);
    addingTag.value = false;
    ElMessage.success('添加标签成功');
    emit('update');
  } catch (error) {
    console.error('添加标签失败:', error);
    ElMessage.error('添加标签失败');
  }
};

// 编辑标签
const editTag = (tag) => {
  editTagForm.value = { ...tag };
  editingTag.value = true;
};

// 取消编辑标签
const cancelEditTag = () => {
  editingTag.value = false;
};

// 更新标签
const updateTag = async () => {
  if (!editTagForm.value.name) {
    ElMessage.warning('请输入标签名称');
    return;
  }
  
  try {
    const updatedTag = await updateTagAPI(editTagForm.value.id, { name: editTagForm.value.name });
    const index = tags.value.findIndex(t => t.id === updatedTag.id);
    if (index !== -1) {
      tags.value[index] = updatedTag;
    }
    editingTag.value = false;
    ElMessage.success('更新标签成功');
    emit('update');
  } catch (error) {
    console.error('更新标签失败:', error);
    ElMessage.error('更新标签失败');
  }
};

// 确认删除标签
const confirmDeleteTag = (tag) => {
  confirmDeleteMessage.value = `确定要删除标签 "${tag.name}" 吗？`;
  deleteCallback.value = () => deleteTag(tag);
  showConfirmDelete.value = true;
};

// 删除标签
const deleteTag = async (tag) => {
  try {
    await deleteTagAPI(tag.id);
    tags.value = tags.value.filter(t => t.id !== tag.id);
    ElMessage.success('删除标签成功');
    emit('update');
  } catch (error) {
    console.error('删除标签失败:', error);
    ElMessage.error('删除标签失败');
  }
};

// 确认删除
const confirmDelete = async () => {
  if (deleteCallback.value) {
    await deleteCallback.value();
  }
  cancelDelete();
};

// 取消删除
const cancelDelete = () => {
  showConfirmDelete.value = false;
  confirmDeleteMessage.value = '';
  deleteCallback.value = null;
};

// 关闭对话框
const closeDialog = () => {
  emit('close');
};
</script>

<style scoped>
.tag-manager {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tag-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.tag-manager-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #909399;
}

.tag-manager-content {
  display: flex;
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.tag-types-section {
  width: 40%;
  padding-right: 20px;
  border-right: 1px solid #ebeef5;
}

.tags-section {
  width: 60%;
  padding-left: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
}

.add-form {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.add-form input {
  width: 100%;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.tag-types-list, .tags-list {
  max-height: 400px;
  overflow-y: auto;
}

.tag-type-item, .tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
}

.tag-type-item:hover, .tag-item:hover {
  background-color: #f5f7fa;
}

.tag-type-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.tag-type-actions, .tag-actions {
  display: flex;
  gap: 5px;
}

.btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
}

.btn-primary {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
  border-color: #f56c6c;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 2px 5px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 400px;
  max-width: 90vw;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.modal input {
  width: 100%;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 15px;
}

.modal .form-actions {
  margin-top: 20px;
}
</style> 