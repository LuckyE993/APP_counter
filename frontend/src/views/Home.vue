<template>
  <div class="container">
    <div class="card">
      <h2 class="text-lg">快速记账</h2>

      <!-- 文本输入 -->
      <div class="form-group">
        <label class="form-label">文本记账</label>
        <div class="input-group">
          <input
            v-model="textInput"
            type="text"
            class="form-input"
            placeholder="例如：午餐 25 微信"
            @keyup.enter="handleTextParse"
          >
          <button @click="handleTextParse" class="btn btn-primary btn-full">
            解析
          </button>
        </div>
      </div>

      <div class="divider">或</div>

      <!-- 图片上传 -->
      <div class="form-group">
        <label class="form-label">截图记账</label>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleImageSelect"
        >
        <button @click="$refs.fileInput.click()" class="btn btn-secondary btn-full btn-camera">
          <span class="btn-icon">📷</span>
          <span class="hidden-mobile">拍照/上传账单</span>
          <span class="hidden-desktop">拍照上传</span>
        </button>
      </div>

      <!-- 图片预览 -->
      <div v-if="imagePreview" class="image-preview">
        <img :src="imagePreview" alt="预览">
        <button @click="clearImage" class="btn-close">×</button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>{{ loadingMessage || '识别中...' }}</p>
      </div>
    </div>

    <!-- 交易表单 -->
    <div v-if="transaction" class="card">
      <h3 class="text-lg">编辑交易</h3>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="form-label">日期</label>
          <input 
            v-model="transaction.date" 
            type="date" 
            class="form-input"
            :class="{ 'error': validationErrors.includes('date') }"
          >
        </div>

        <div class="form-group">
          <label class="form-label">金额</label>
          <input 
            v-model.number="transaction.amount" 
            type="number" 
            step="0.01" 
            class="form-input" 
            :class="{ 'error': validationErrors.includes('amount') }"
            placeholder="0.00"
          >
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">商家/描述</label>
        <input 
          v-model="transaction.merchant" 
          type="text" 
          class="form-input" 
          :class="{ 'error': validationErrors.includes('merchant') }"
          placeholder="输入商家名称"
        >
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="form-label">支付方式</label>
          <select 
            v-model="transaction.payment_method" 
            class="form-input"
            :class="{ 'error': validationErrors.includes('payment_method') }"
          >
            <option value="">请选择</option>
            <option v-for="method in accountConfig.payment_methods" :key="method.value" :value="method.value">
              {{ method.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">类型</label>
          <select v-model="transaction.transaction_type" class="form-input">
            <option value="expense">支出</option>
            <option value="income">收入</option>
          </select>
        </div>
      </div>

      <!-- 如果选择了银行卡，显示银行卡选择 -->
      <div v-if="transaction.payment_method === '银行卡'" class="form-group">
        <label class="form-label">选择银行卡</label>
        <select 
          v-model="selectedBankCard" 
          @change="updateBankCard" 
          class="form-input"
          :class="{ 'error': validationErrors.includes('bank_card') }"
        >
          <option value="">请选择银行卡</option>
          <option v-for="card in accountConfig.bank_cards" :key="card.account" :value="card.account">
            {{ card.bank_name }} ({{ card.last_four }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">分类</label>
        <select 
          v-model="transaction.category" 
          class="form-input"
          :class="{ 'error': validationErrors.includes('category') }"
        >
          <option value="">请选择分类</option>
          <optgroup 
            v-if="transaction.transaction_type === 'expense'" 
            v-for="(categories, group) in groupedExpenseCategories" 
            :key="group" 
            :label="group"
          >
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </option>
          </optgroup>
          <option 
            v-if="transaction.transaction_type === 'income'"
            v-for="cat in accountConfig.income_categories" 
            :key="cat.value" 
            :value="cat.value"
          >
            {{ cat.label }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">备注</label>
        <input v-model="transaction.description" type="text" class="form-input" placeholder="可选">
      </div>

      <div class="flex">
        <button @click="handleSave" class="btn btn-primary" style="flex: 1;">
          💾 保存
        </button>
        <button @click="handleCancel" class="btn btn-secondary" style="flex: 1;">
          ❌ 取消
        </button>
      </div>
    </div>

    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <div v-for="line in errorMessage.split('\n')" :key="line">{{ line }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { parseImage, parseText, saveTransaction, getAccountConfig } from '../api'

const textInput = ref('')
const fileInput = ref(null)
const imagePreview = ref(null)
const loading = ref(false)
const transaction = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
const selectedBankCard = ref('')
const validationErrors = ref([])

// 账户配置数据
const accountConfig = ref({
  payment_methods: [],
  bank_cards: [],
  expense_categories: [],
  income_categories: [],
  liability_accounts: []
})

// 根据分类分组
const groupedExpenseCategories = ref({})

// 组件加载时获取账户配置
onMounted(async () => {
  try {
    const config = await getAccountConfig()
    accountConfig.value = config
    updateGroupedCategories()
  } catch (error) {
    console.error('Failed to load account config:', error)
  }
})

// 监听配置变化，更新分组
watch(() => accountConfig.value.expense_categories, () => {
  updateGroupedCategories()
}, { deep: true })

const updateGroupedCategories = () => {
  const grouped = {}
  accountConfig.value.expense_categories.forEach(cat => {
    if (!grouped[cat.group]) {
      grouped[cat.group] = []
    }
    grouped[cat.group].push(cat)
  })
  groupedExpenseCategories.value = grouped
}

const updateBankCard = () => {
  if (selectedBankCard.value && transaction.value) {
    const card = accountConfig.value.bank_cards.find(c => c.account === selectedBankCard.value)
    if (card) {
      transaction.value.bank_name = card.bank
      transaction.value.card_last_four = card.last_four
    }
  }
}

// 根据VLM返回的银行信息自动选择银行卡
const autoSelectBankCard = (result) => {
  if (result.payment_method === '银行卡' && result.bank_name && result.card_last_four) {
    // 查找匹配的银行卡
    const card = accountConfig.value.bank_cards.find(
      c => c.bank === result.bank_name && c.last_four === result.card_last_four
    )
    if (card) {
      selectedBankCard.value = card.account
    }
  } else {
    // 非银行卡支付，清空选择
    selectedBankCard.value = ''
  }
}

const getTodayDate = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

const handleTextParse = async () => {
  if (!textInput.value.trim()) return

  loading.value = true
  errorMessage.value = ''

  try {
    const result = await parseText(textInput.value)
    transaction.value = {
      ...result,
      date: result.date === '今天' ? getTodayDate() : result.date
    }
    // 自动选择银行卡
    autoSelectBankCard(result)
    textInput.value = ''
  } catch (error) {
    errorMessage.value = '解析失败: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    loading.value = false
  }
}

const handleImageSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  // 压缩并解析
  loading.value = true
  errorMessage.value = ''

  try {
    const base64 = await compressImage(file)
    const result = await parseImage(base64.split(',')[1])
    transaction.value = result
    // 自动选择银行卡
    autoSelectBankCard(result)
  } catch (error) {
    errorMessage.value = '识别失败: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    loading.value = false
  }
}

const compressImage = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let width = img.width
        let height = img.height

        const maxSize = 1024
        if (width > height && width > maxSize) {
          height = (height * maxSize) / width
          width = maxSize
        } else if (height > maxSize) {
          width = (width * maxSize) / height
          height = maxSize
        }

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', 0.8))
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

const clearImage = () => {
  imagePreview.value = null
  fileInput.value.value = ''
}

const validateTransaction = () => {
  const errors = []
  validationErrors.value = []
  
  if (!transaction.value.date) {
    errors.push('请选择日期')
    validationErrors.value.push('date')
  }
  
  if (!transaction.value.amount || transaction.value.amount <= 0) {
    errors.push('请输入有效金额')
    validationErrors.value.push('amount')
  }
  
  if (!transaction.value.merchant?.trim()) {
    errors.push('请输入商家/描述')
    validationErrors.value.push('merchant')
  }
  
  if (!transaction.value.payment_method) {
    errors.push('请选择支付方式')
    validationErrors.value.push('payment_method')
  }
  
  if (transaction.value.payment_method === '银行卡' && !selectedBankCard.value) {
    errors.push('请选择银行卡')
    validationErrors.value.push('bank_card')
  }
  
  if (!transaction.value.category) {
    errors.push('请选择分类')
    validationErrors.value.push('category')
  }
  
  return errors
}

const handleSave = async () => {
  const validationErrors = validateTransaction()
  
  if (validationErrors.length > 0) {
    errorMessage.value = '请完善以下信息：\n' + validationErrors.join('\n')
    setTimeout(() => errorMessage.value = '', 4000)
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await saveTransaction(transaction.value)
    successMessage.value = '保存成功！'
    setTimeout(() => successMessage.value = '', 2000)
    transaction.value = null
    selectedBankCard.value = ''
    clearImage()
  } catch (error) {
    errorMessage.value = '保存失败: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  transaction.value = null
  selectedBankCard.value = ''
  validationErrors.value = []
  clearImage()
}
</script>

<style scoped>
/* 表单验证错误样式 */
.form-input.error {
  border-color: #f44336;
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2);
}

.form-input.error:focus {
  border-color: #f44336;
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.3);
}

/* 输入组合 */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (min-width: 768px) {
  .input-group {
    flex-direction: row;
    align-items: flex-end;
  }
  
  .input-group .form-input {
    flex: 1;
  }
  
  .input-group .btn {
    flex-shrink: 0;
    margin-left: 0.5rem;
  }
}

/* 分隔线 */
.divider {
  text-align: center;
  margin: 1rem 0;
  color: #999;
  font-size: 0.875rem;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e0e0e0;
  z-index: 1;
}

.divider::after {
  content: attr(data-text);
  background: white;
  padding: 0 1rem;
  position: relative;
  z-index: 2;
}

/* 按钮样式 */
.btn-full {
  width: 100%;
}

.btn-camera {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-icon {
  font-size: 1.25rem;
}

@media (min-width: 768px) {
  .btn-icon {
    font-size: 1.5rem;
  }
}

/* 图片预览 */
.image-preview {
  position: relative;
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  background: #f5f5f5;
}

@media (min-width: 768px) {
  .image-preview img {
    max-height: 400px;
  }
}

.btn-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.6);
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.btn-close:hover {
  background: rgba(0,0,0,0.8);
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 2rem 1rem;
}

.loading p {
  font-size: 0.875rem;
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 1rem;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4DBA87;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@media (min-width: 768px) {
  .spinner {
    width: 40px;
    height: 40px;
    border-width: 4px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 消息提示 */
.success-message,
.error-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 1000;
  font-size: 0.875rem;
  max-width: 90vw;
  text-align: center;
}

@media (min-width: 768px) {
  .success-message,
  .error-message {
    padding: 1rem 2rem;
    font-size: 1rem;
    max-width: 400px;
  }
}

.success-message {
  background: #4DBA87;
  color: white;
}

.error-message {
  background: #f44336;
  color: white;
}

/* 表单优化 */
.form-group {
  margin-bottom: 1rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

/* 选择框优化 */
select.form-input {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
  appearance: none;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .btn {
    min-height: 48px;
  }
  
  .form-input {
    min-height: 48px;
  }
  
  .btn-close {
    width: 2.5rem;
    height: 2.5rem;
  }
}


<style scoped>
.modal-overlay {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 1000;
}

/* 大屏幕优化 */
@media (min-width: 768px) {
  .card {
    margin-bottom: 2rem;
  }
  
  .grid-2 {
    gap: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .btn-full {
    max-width: 300px;
    margin: 0 auto;
    display: flex;
  }
}

@media (min-width: 1024px) {
  .container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 3rem;
    align-items: start;
    justify-content: center;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  /* 当只有一个子元素时居中显示 */
  .container:has(> :last-child:nth-child(1)) {
    display: flex;
    justify-content: center;
  }
  
  .container:has(> :last-child:nth-child(1)) .card {
    max-width: 600px;
  }

  .card:first-child {
    position: sticky;
    top: 2rem;
  }
}
</style>