<template>
  <div class="operator-manage">
    <div class="page-header">
      <h1>操作员管理</h1>
      <button @click="openAddModal" class="add-btn">
        + 新增操作员
      </button>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <button @click="handleDelete(user)" class="delete-btn">
                删除
              </button>
            </td>
          </tr>
          <tr v-if="!loading && users.length === 0">
            <td colspan="5" class="empty-row">暂无操作员数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>新增操作员</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="handleAddUser" class="modal-body">
          <div class="form-group">
            <label>用户名 *</label>
            <input
              v-model="formData.username"
              type="text"
              required
              placeholder="请输入用户名"
            />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="请输入邮箱（可选）"
            />
          </div>
          <div class="form-group">
            <label>密码 *</label>
            <input
              v-model="formData.password"
              type="password"
              required
              placeholder="请输入密码"
            />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              取消
            </button>
            <button type="submit" class="confirm-btn" :disabled="loading">
              {{ loading ? '创建中...' : '确认创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const formData = ref({
  username: '',
  email: '',
  password: ''
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('获取操作员列表失败:', error)
    alert('获取操作员列表失败')
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  formData.value = { username: '', email: '', password: '' }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const handleAddUser = async () => {
  loading.value = true
  try {
    await api.post('/admin/users', formData.value)
    alert('创建成功')
    closeModal()
    await fetchUsers()
  } catch (error) {
    console.error('创建操作员失败:', error)
    alert(error.response?.data?.error || '创建操作员失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (user) => {
  if (!confirm(`确定要删除操作员 "${user.username}" 吗？`)) {
    return
  }
  
  try {
    await api.delete(`/admin/users/${user.id}`)
    alert('删除成功')
    await fetchUsers()
  } catch (error) {
    console.error('删除操作员失败:', error)
    alert(error.response?.data?.error || '删除操作员失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.operator-manage {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  color: #2c3e50;
  margin: 0;
}

.add-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: #2980b9;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  color: #2c3e50;
  font-weight: 600;
  font-size: 14px;
}

.data-table td {
  color: #555;
  font-size: 14px;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.delete-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.delete-btn:hover {
  background: #c0392b;
}

.empty-row {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 20px;
  background: #ecf0f1;
  color: #333;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #bdc3c7;
}

.confirm-btn {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.confirm-btn:hover:not(:disabled) {
  background: #2980b9;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
