<template>
  <div class="profile-container">
    <h2>修改密码</h2>
    <div class="password-form">
      <div class="form-group">
        <label for="old-password">旧密码</label>
        <input 
          type="password" 
          id="old-password" 
          v-model="passwordForm.oldPassword"
          placeholder="请输入旧密码" 
        />
      </div>
      
      <div class="form-group">
        <label for="new-password">新密码</label>
        <input 
          type="password" 
          id="new-password" 
          v-model="passwordForm.newPassword"
          placeholder="请输入新密码" 
        />
      </div>
      
      <div class="form-group">
        <label for="confirm-password">确认新密码</label>
        <input 
          type="password" 
          id="confirm-password" 
          v-model="passwordForm.confirmPassword"
          placeholder="请再次输入新密码" 
        />
      </div>
      
      <div class="form-tip">
        <p>提示：修改密码后将重新登录系统</p>
      </div>
      
      <div class="form-actions">
        <button 
          class="btn-submit" 
          @click="handleChangePassword"
          :disabled="loading"
        >
          {{ loading ? '提交中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../../store/auth';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { logUserOperation, OperationType } from '../../utils/logger';

const authStore = useAuthStore();
const router = useRouter();
const loading = ref(false);

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const handleChangePassword = async () => {
  // 表单验证
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入旧密码');
    return;
  }
  
  if (!passwordForm.value.newPassword) {
    ElMessage.warning('请输入新密码');
    return;
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致');
    return;
  }
  
  try {
    loading.value = true;
    await authStore.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    );
    
    // 记录修改密码操作
    logUserOperation(OperationType.CHANGE_PASSWORD);
    
    ElMessage.success('密码修改成功，请重新登录');
    
    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    
    // 退出登录并跳转到登录页
    setTimeout(async () => {
      await authStore.logout();
      router.push('/login');
    }, 1500);
    
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '密码修改失败';
    ElMessage.error(errorMsg);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.password-form {
  max-width: 500px;
  margin: 20px auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-tip {
  margin: 15px 0;
  color: #e6a23c;
  font-size: 14px;
}

.form-actions {
  margin-top: 20px;
}

.btn-submit {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-submit:hover {
  background-color: #66b1ff;
}

.btn-submit:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
</style> 