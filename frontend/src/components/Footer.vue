<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p>© {{ currentYear }} Just For Fun - 编程系统</p>
      <p class="license">
        <span class="license-link" @click="showLicense">MIT License - MIT 许可证</span>
      </p>
    </div>
    
    <!-- LICENSE 弹窗 -->
    <div v-if="licenseVisible" class="license-modal-overlay" @click="licenseVisible = false">
      <div class="license-modal" @click.stop>
        <h3>MIT License</h3>
        <div class="license-content">
          <p>Copyright (c) {{ currentYear }} wangyanjun13</p>
          <p>
            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:
          </p>
          <p>
            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.
          </p>
          <p>
            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.
          </p>
        </div>
        <button @click="licenseVisible = false">关闭</button>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue';

// 计算当前年份，用于版权信息
const currentYear = computed(() => new Date().getFullYear());

// LICENSE 弹窗控制
const licenseVisible = ref(false);
const showLicense = () => {
  licenseVisible.value = true;
};
</script>

<style scoped>
.app-footer {
  padding: 15px 0;
  background-color: #1890ff;
  color: white;
  text-align: center;
  font-size: 14px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-content p {
  margin: 5px 0;
}

.license {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.license-link {
  cursor: pointer;
  text-decoration: underline;
}

.license-link:hover {
  color: #fff;
}

/* LICENSE 弹窗样式 */
.license-modal-overlay {
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

.license-modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  color: #333;
}

.license-modal h3 {
  margin-top: 0;
  color: #1890ff;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.license-content {
  margin: 20px 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.license-modal button {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  float: right;
}

.license-modal button:hover {
  background-color: #40a9ff;
}
</style> 