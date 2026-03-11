<template>
  <div class="device-select-container">
    <div class="device-select-box">
      <h2>选择设备</h2>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="devices.length === 0" class="empty-state">
        <p>暂无可用设备，请联系管理员添加。</p>
        <button @click="loadDevices" class="refresh-btn">刷新</button>
      </div>

      <div v-else>
        <div class="device-list">
          <div
            v-for="device in devices"
            :key="device.id"
            class="device-card"
            :class="{ selected: selectedIds.includes(device.id) }"
          >
            <input
              type="checkbox"
              :value="device.id"
              v-model="selectedIds"
              class="device-checkbox"
            />
            <div class="device-info" @click="toggleSelect(device.id)">
              <h3>{{ device.device_name || device.device_id }}</h3>
              <div class="info-item">
                <span class="label">设备 ID:</span>
                <span class="value">{{ device.device_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">订阅主题:</span>
                <span class="value">{{ device.subscribe_topic }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="action-bar">
          <button @click="goToRemote" :disabled="selectedIds.length === 0">
            遥控选中设备 ({{ selectedIds.length }})
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const devices = ref([])
const selectedIds = ref([])

const loadDevices = async () => {
  loading.value = true
  try {
    await userStore.fetchDevices()
    devices.value = userStore.devices
  } catch (error) {
    console.error('Failed to load devices:', error)
  } finally {
    loading.value = false
  }
}

const toggleSelect = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const goToRemote = () => {
  if (selectedIds.value.length === 0) return
  router.push({
    path: '/remote',
    query: { devices: selectedIds.value.join(',') }
  })
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.device-select-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.device-select-box {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 800px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.refresh-btn {
  padding: 10px 20px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.refresh-btn:hover {
  background: #1976d2;
}

.device-list {
  display: grid;
  gap: 15px;
  margin-bottom: 20px;
}

.device-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  transition: all 0.2s;
}

.device-card.selected {
  border-color: #2196f3;
  background-color: #e3f2fd;
}

.device-checkbox {
  margin-right: 15px;
  margin-top: 5px;
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.device-info {
  flex: 1;
}

.device-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.info-item {
  display: flex;
  gap: 10px;
  font-size: 14px;
  margin-top: 5px;
}

.info-item .label {
  color: #666;
  min-width: 80px;
}

.info-item .value {
  color: #333;
  font-family: monospace;
}

.action-bar {
  text-align: center;
}

.action-bar button {
  padding: 12px 30px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.action-bar button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>