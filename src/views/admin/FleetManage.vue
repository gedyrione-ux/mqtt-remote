<template>
  <div class="fleet-manage">
    <div class="page-header">
      <h1>装备车辆库</h1>
      <button @click="openAddModal" class="add-btn">
        + 录入新车辆
      </button>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>车号</th>
            <th>车辆名称</th>
            <th>硬件地址码</th>
            <th>当前所属操作员</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in devices" :key="device.id">
            <td><strong>{{ device.device_id }}</strong></td>
            <td>{{ device.device_name || '-' }}</td>
            <td><span class="code-tag">{{ device.device_code }}</span></td>
            <td>
              <span :class="{ 'text-muted': !device.owner_name }">
                {{ device.owner_name || '未分配' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <div class="assign-dropdown" v-if="assigningId === device.id">
                  <select
                    v-model="selectedUserId"
                    @change="handleAssign(device)"
                    @blur="cancelAssign"
                    ref="assignSelect"
                    class="assign-select"
                  >
                    <option :value="null">-- 请选择操作员 --</option>
                    <option v-for="user in allUsers" :key="user.id" :value="user.id">
                      {{ user.username }}
                    </option>
                  </select>
                </div>
                <button
                  v-else
                  @click="startAssign(device)"
                  class="assign-btn"
                >
                  授权调配
                </button>
                <button @click="handleDelete(device)" class="delete-btn">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!loading && devices.length === 0">
            <td colspan="5" class="empty-row">暂无车辆数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>录入新抑尘车</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="handleAddDevice" class="modal-body">
          <div class="form-group">
            <label>车号 (device_id) *</label>
            <input
              v-model="formData.device_id"
              type="text"
              required
              placeholder="例如: device001"
            />
          </div>
          <div class="form-group">
            <label>车辆名称</label>
            <input
              v-model="formData.device_name"
              type="text"
              placeholder="例如: A矿区1号抑尘车"
            />
          </div>
          <div class="form-group">
            <label>硬件地址码 (device_code) *</label>
            <input
              v-model.number="formData.device_code"
              type="number"
              required
              placeholder="例如: 2"
            />
          </div>
          <div class="form-group">
            <label>设备用户名 (device_username) *</label>
            <input
              v-model="formData.device_username"
              type="text"
              required
              placeholder="设备登录用户名"
            />
          </div>
          <div class="form-group">
            <label>设备密码 (device_password) *</label>
            <input
              v-model="formData.device_password"
              type="text"
              required
              placeholder="设备登录密码"
            />
          </div>
          <div class="form-group">
            <label>发布主题 (publish_topic) *</label>
            <input
              v-model="formData.publish_topic"
              type="text"
              required
              placeholder="例如: device/device001/pub"
            />
          </div>
          <div class="form-group">
            <label>订阅主题 (subscribe_topic) *</label>
            <input
              v-model="formData.subscribe_topic"
              type="text"
              required
              placeholder="例如: device/device001/sub"
            />
          </div>
          <div class="form-group">
            <label>分配给操作员</label>
            <select v-model="formData.user_id" class="form-select">
              <option :value="null">-- 不分配（默认管理员）--</option>
              <option v-for="user in allUsers" :key="user.id" :value="user.id">
                {{ user.username }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              取消
            </button>
            <button type="submit" class="confirm-btn" :disabled="loading">
              {{ loading ? '录入中...' : '确认录入' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../../services/api'

const devices = ref([])
const allUsers = ref([])
const loading = ref(false)
const showModal = ref(false)
const assigningId = ref(null)
const selectedUserId = ref(null)
const assignSelect = ref(null)

const formData = ref({
  device_id: '',
  device_name: '',
  device_code: 2,
  device_username: '',
  device_password: '',
  publish_topic: '',
  subscribe_topic: '',
  user_id: null
})

const fetchDevices = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/devices')
    devices.value = response.data
  } catch (error) {
    console.error('获取车辆列表失败:', error)
    alert('获取车辆列表失败')
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/admin/users')
    allUsers.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const openAddModal = () => {
  formData.value = {
    device_id: '',
    device_name: '',
    device_code: 2,
    device_username: '',
    device_password: '',
    publish_topic: '',
    subscribe_topic: '',
    user_id: null
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const handleAddDevice = async () => {
  loading.value = true
  try {
    const data = { ...formData.value }
    if (!data.user_id) delete data.user_id
    await api.post('/admin/devices', data)
    alert('录入成功')
    closeModal()
    await fetchDevices()
  } catch (error) {
    console.error('录入车辆失败:', error)
    alert(error.response?.data?.error || '录入车辆失败')
  } finally {
    loading.value = false
  }
}

const startAssign = async (device) => {
  await fetchUsers()
  assigningId.value = device.id
  selectedUserId.value = device.owner_id
  await nextTick()
  if (assignSelect.value) {
    assignSelect.value.focus()
  }
}

const cancelAssign = () => {
  assigningId.value = null
  selectedUserId.value = null
}

const handleAssign = async (device) => {
  if (selectedUserId.value === device.owner_id) {
    cancelAssign()
    return
  }
  
  try {
    await api.put(`/admin/devices/${device.id}`, {
      user_id: selectedUserId.value
    })
    alert('授权调配成功')
    await fetchDevices()
  } catch (error) {
    console.error('授权调配失败:', error)
    alert(error.response?.data?.error || '授权调配失败')
  } finally {
    cancelAssign()
  }
}

const handleDelete = async (device) => {
  if (!confirm(`确定要删除车辆 "${device.device_id}" 吗？`)) {
    return
  }
  
  try {
    await api.delete(`/admin/devices/${device.id}`)
    alert('删除成功')
    await fetchDevices()
  } catch (error) {
    console.error('删除车辆失败:', error)
    alert(error.response?.data?.error || '删除车辆失败')
  }
}

onMounted(() => {
  fetchDevices()
  fetchUsers()
})
</script>

<style scoped>
.fleet-manage {
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
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: #229954;
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

.code-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #3498db;
  color: white;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.text-muted {
  color: #999;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.assign-btn {
  background: #f39c12;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.assign-btn:hover {
  background: #e67e22;
}

.assign-select {
  padding: 6px 10px;
  border: 1px solid #f39c12;
  border-radius: 4px;
  font-size: 13px;
  background: white;
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
  overflow-y: auto;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 100%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
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

.form-group input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-select:focus {
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
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.confirm-btn:hover:not(:disabled) {
  background: #229954;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
