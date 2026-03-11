<template>
  <div class="panel">
    <div class="header-row">
      <button @click="goBackToDevices" class="back-button">⬅️ 设备列表</button>
      <h2>{{ isMultiDevice ? '📡 多设备遥控器' : '📡 4G 设备遥控器' }}</h2>
      <div class="header-right"></div>
    </div>

    <template v-if="!isMultiDevice && currentSingleDevice">
      <div class="status-bar">
        <div class="left-placeholder"></div>
        <div class="device-info">
          <span class="device-name">{{ currentSingleDevice.device_name || currentSingleDevice.device_id }}</span>
        </div>
        <div class="conn-section">
          <div class="conn-indicator">
            <span class="led" :class="connLedClass"></span>
          </div>
          <button @click="toggleConnection" :disabled="connecting">
            <i v-if="connecting" class="fas fa-spinner fa-spin"></i>
            {{ buttonText }}
          </button>
        </div>
      </div>

      <div class="button-grid">
        <button @click="sendCommand('1')">连通阀 开</button>
        <button @click="sendCommand('2')">喷水阀 开</button>
        <button @click="sendCommand('3')">连通阀 关</button>
        <button @click="sendCommand('4')">喷水阀 关</button>
        <button @click="sendCommand('5')">炮头 上</button>
        <button @click="sendCommand('6')">炮头 下</button>
        <button @click="sendCommand('7')">炮头 左</button>
        <button @click="sendCommand('8')">炮头 右</button>
      </div>

      <div class="device-status">
        <div class="status-item">
          <div>连通阀</div>
          <div class="led" :class="valveConnectClass"></div>
          <div>{{ valveConnectText }}</div>
        </div>
        <div class="status-item">
          <div>喷水阀</div>
          <div class="led" :class="valveSprayClass"></div>
          <div>{{ valveSprayText }}</div>
        </div>
      </div>
    </template>

    <template v-else-if="isMultiDevice">
      <div class="multi-connect-bar">
        <button @click="toggleConnection" :disabled="connecting">
          <i v-if="connecting" class="fas fa-spinner fa-spin"></i>
          {{ buttonText }}
        </button>
      </div>

      <div class="button-grid">
        <button @click="sendCommand('1')">连通阀 开</button>
        <button @click="sendCommand('2')">喷水阀 开</button>
        <button @click="sendCommand('3')">连通阀 关</button>
        <button @click="sendCommand('4')">喷水阀 关</button>
        <button @click="sendCommand('5')">炮头 上</button>
        <button @click="sendCommand('6')">炮头 下</button>
        <button @click="sendCommand('7')">炮头 左</button>
        <button @click="sendCommand('8')">炮头 右</button>
      </div>

      <div class="device-table-wrapper">
        <table class="device-table">
          <thead>
            <tr>
              <th>设备名称</th>
              <th>连接状态</th>
              <th>喷水阀</th>
              <th>连通阀</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dev in devices" :key="dev.id">
              <td>{{ dev.device_name || dev.device_id }}</td>
              <td>
                <span class="status-led" :class="connectionClass(dev.id)"></span>
                {{ connectionText(dev.id) }}
              </td>
              <td>
                <span class="status-led" :class="valveClass(devStates[dev.id]?.spray)"></span>
                {{ valveText(devStates[dev.id]?.spray) }}
              </td>
              <td>
                <span class="status-led" :class="valveClass(devStates[dev.id]?.connect)"></span>
                {{ valveText(devStates[dev.id]?.connect) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else class="no-device">没有选中任何设备</div>

    <div class="feedback">
      <div v-for="(msg, index) in localMessages" :key="index">{{ msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMqtt } from '../composables/useMqtt'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const MQTT_SERVER = import.meta.env.VITE_MQTT_WS_URL
const MULTI_PUBLISH_TOPIC = 'command'

const deviceIds = computed(() => {
  const ids = route.query.devices
  return ids ? ids.split(',').map(Number) : []
})

const allDevices = computed(() => userStore.devices || [])
const devices = computed(() => allDevices.value.filter(d => deviceIds.value.includes(d.id)))

const isMultiDevice = computed(() => devices.value.length > 1)
const currentSingleDevice = computed(() => devices.value[0] || null)

// 多设备响应记录
const respondedDevices = ref(new Set())
const totalDevices = ref(0)

const localConnected = ref(false)
const localMessages = ref([])
const connecting = ref(false)
const deviceConfirmed = ref(false) // 仅用于单设备

let confirmTimeout = null
let mqttApi = ref(null)

const devStates = reactive({})
let heartbeatInterval = null

const valveConnectState = ref(null)
const valveSprayState = ref(null)

const addMessage = (msg) => {
  const time = new Date().toLocaleTimeString()
  localMessages.value.unshift(`[${time}] ${msg}`)
  if (localMessages.value.length > 20) localMessages.value.pop()
}

// 处理设备反馈消息，通过主题区分设备
const handleDeviceMessage = (topic, payload) => {
  const bytes = new Uint8Array(payload)
  console.log('📨 收到原始消息，主题:', topic, '数据:', Array.from(bytes).map(b => b.toString(16).padStart(2,'0')).join(' '))

  if (bytes.length < 5 || bytes[0] !== 0x52) return

  // 通过主题匹配设备
  const targetDev = devices.value.find(d => d.subscribe_topic === topic)
  if (!targetDev) {
    console.log('❌ 未找到匹配主题的设备，忽略此消息')
    return
  }
  console.log('✅ 匹配到设备:', targetDev.device_id, '主题:', topic)

  if (isMultiDevice.value) {
    // 多设备：更新对应设备的状态
    let state = devStates[targetDev.id]
    if (!state) {
      state = { spray: null, connect: null, lastSeen: 0 }
      devStates[targetDev.id] = state
    }
    const valveConn = bytes[2]
    state.connect = valveConn === 0x4F ? 'O' : (valveConn === 0x43 ? 'C' : (valveConn === 0x49 ? 'I' : null))
    const valveSpray = bytes[3]
    state.spray = valveSpray === 0x4F ? 'O' : (valveSpray === 0x43 ? 'C' : (valveSpray === 0x49 ? 'I' : null))
    state.lastSeen = Date.now()
    devStates[targetDev.id] = { ...state }

    // 记录该设备已响应
    respondedDevices.value.add(targetDev.id)
    console.log('📋 已响应设备:', Array.from(respondedDevices.value))

    // 检查是否所有设备都已响应
    if (respondedDevices.value.size === totalDevices.value && connecting.value && !localConnected.value) {
      localConnected.value = true
      connecting.value = false
      addMessage('✅ 所有设备响应，连接成功')
      if (confirmTimeout) clearTimeout(confirmTimeout)
    }
  } else {
    // 单设备模式：直接更新状态，主题已匹配
    const valveConn = bytes[2]
    valveConnectState.value = valveConn === 0x4F ? 'O' : (valveConn === 0x43 ? 'C' : (valveConn === 0x49 ? 'I' : null))
    const valveSpray = bytes[3]
    valveSprayState.value = valveSpray === 0x4F ? 'O' : (valveSpray === 0x43 ? 'C' : (valveSpray === 0x49 ? 'I' : null))

    if (!deviceConfirmed.value && !localConnected.value) {
      deviceConfirmed.value = true
      addMessage('✅ 设备响应确认')
      if (connecting.value) {
        finishConnection(true)
      }
    }
  }
}

const initMqtt = () => {
  if (devices.value.length === 0) return

  const firstDev = devices.value[0]
  const options = {
    server: MQTT_SERVER,
    username: firstDev?.device_username || null,
    password: firstDev?.device_password || null,
    clientId: 'vue_remote_' + Math.random().toString(16).substr(2, 6),
    publishTopic: isMultiDevice.value ? MULTI_PUBLISH_TOPIC : firstDev?.publish_topic,
    subscribeTopics: devices.value.map(dev => dev.subscribe_topic).filter(Boolean),
    onMessage: handleDeviceMessage,
    onConnect: () => {
      console.log('🔥🔥🔥 RemoteController: onConnect 触发');
      addMessage('✅ MQTT服务器连接成功')
      
      if (isMultiDevice.value) {
        console.log('🟢 多设备分支，统一主题:', MULTI_PUBLISH_TOPIC);
        totalDevices.value = devices.value.length
        respondedDevices.value.clear()
        sendQueryMulti()
        confirmTimeout = setTimeout(() => {
          if (connecting.value) {
            const unresponded = devices.value.filter(dev => !respondedDevices.value.has(dev.id))
            if (unresponded.length > 0) {
              console.log('⏰ 超时，未响应设备:', unresponded.map(d => d.device_id).join(', '))
              addMessage('❌ 部分设备响应超时，连接失败')
              finishConnection(false)
            } else {
              finishConnection(true)
            }
          }
        }, 10000)
      } else {
        console.log('🟢 单设备分支，即将调用 startDeviceConfirmation');
        startDeviceConfirmation()
      }
    },
    onDisconnect: () => {
      localConnected.value = false
      deviceConfirmed.value = false
      connecting.value = false
      respondedDevices.value.clear()
      totalDevices.value = 0
      addMessage('🔌 MQTT断开')
    },
    onMessageAdd: addMessage,
  }
  mqttApi.value = useMqtt(options)
}

const connect = () => mqttApi.value?.connect()
const disconnect = () => {
  mqttApi.value?.disconnect()
  localConnected.value = false
  deviceConfirmed.value = false
  respondedDevices.value.clear()
  totalDevices.value = 0
  if (confirmTimeout) {
    clearTimeout(confirmTimeout)
    confirmTimeout = null
  }
}

const publish = (topic, message) => mqttApi.value?.publish(topic, message)

const goBackToDevices = () => {
  disconnect()
  router.push('/devices')
}

// 💥 【核心修改 1】多设备发送查询指令（交由 Python 总路由处理）
const sendQueryMulti = () => {
  console.log('📤 sendQueryMulti 被调用');
  const modelCode = 0x44
  const placeholder = 0x00 // 占位符，将被 Python 替换为真实地址码
  const keyCode = 'A'.charCodeAt(0)
  const para = 0x00
  const term = 0x0D
  const commandBytes = new Uint8Array([modelCode, placeholder, keyCode, para, term])

  // 转换为 Base64
  let binaryString = ''
  for (let i = 0; i < commandBytes.length; i++) {
    binaryString += String.fromCharCode(commandBytes[i])
  }
  const cmdBase64 = btoa(binaryString)

  // 构造纯粹、干净的 JSON payload 发给 Python
  const payload = {
    targets: devices.value.map(dev => ({
      id: dev.device_id,
      device_code: dev.device_code || 2
    })),
    cmd_template: cmdBase64
  }

  console.log('📤 发送查询指令到总路由:', MULTI_PUBLISH_TOPIC, 'payload:', payload)
  publish(MULTI_PUBLISH_TOPIC, JSON.stringify(payload))
}

// 单设备发送查询指令（直接发给设备，不经过 Python 路由）
const sendQueryToDevice = (device) => {
  console.log('📤 sendQueryToDevice 被调用，设备:', device.device_id);
  const modelCode = 0x44
  const devCode = device.device_code || 0x02
  const keyCode = 'A'.charCodeAt(0)
  const para = 0x00
  const term = 0x0D
  const bytes = new Uint8Array([modelCode, devCode, keyCode, para, term])

  console.log('📤 发送查询指令到设备:', device.device_id, '主题:', device.publish_topic, '数据:', Array.from(bytes).map(b => b.toString(16).padStart(2,'0')).join(' '))
  publish(device.publish_topic, bytes)
}

const startDeviceConfirmation = () => {
  console.log('🚀 startDeviceConfirmation 被调用');
  deviceConfirmed.value = false
  addMessage('⏳ 等待设备响应...')
  if (currentSingleDevice.value) {
    sendQueryToDevice(currentSingleDevice.value)
  }

  confirmTimeout = setTimeout(() => {
    console.log('⏰ 超时触发，deviceConfirmed =', deviceConfirmed.value)
    if (!deviceConfirmed.value) {
      addMessage('❌ 设备响应超时，请检查设备是否在线')
      finishConnection(false)
    }
  }, 5000)
}

const finishConnection = (success) => {
  console.log('🏁 finishConnection, success =', success)
  connecting.value = false
  if (success) {
    localConnected.value = true
    addMessage('✅ 连接成功')
  } else {
    if (mqttApi.value) {
      mqttApi.value.disconnect()
    }
    localConnected.value = false
  }
  if (confirmTimeout) {
    clearTimeout(confirmTimeout)
    confirmTimeout = null
  }
}

const toggleConnection = () => {
  if (localConnected.value) {
    disconnect()
  } else {
    if (mqttApi.value?.connected.value) {
      console.log('MQTT 已连接但状态未同步，先断开再重连')
      mqttApi.value.disconnect()
      setTimeout(() => {
        connecting.value = true
        connect()
      }, 100)
    } else {
      connecting.value = true
      connect()
    }
  }
}

// 💥 【核心修改 2】多设备/单设备 控制指令发送
const sendCommand = (key) => {
  if (!localConnected.value) {
    addMessage('❌ 请先连接')
    return
  }

  // 1. 构造原始指令字节（模板地址码用 0x00 占位）
  const modelCode = 0x44
  const placeholder = 0x00 // 占位符，将被 Python 替换为真实地址码
  const keyCode = key.charCodeAt(0)
  const para = 0x00
  const term = 0x0D
  const commandBytes = new Uint8Array([modelCode, placeholder, keyCode, para, term])

  // 2. 将字节数组转换为 Base64 字符串
  let binaryString = ''
  for (let i = 0; i < commandBytes.length; i++) {
    binaryString += String.fromCharCode(commandBytes[i])
  }
  const cmdBase64 = btoa(binaryString)

  // 3. 构造极简的 JSON payload 给 Python
  const payload = {
    targets: devices.value.map(dev => ({
      id: dev.device_id,
      device_code: dev.device_code || 2
    })),
    cmd_template: cmdBase64
  }

  console.log('📤 发送指令到总路由:', MULTI_PUBLISH_TOPIC, 'payload:', payload)
  publish(MULTI_PUBLISH_TOPIC, JSON.stringify(payload))
}

const connLedClass = computed(() => {
  if (connecting.value) return 'gray'
  return localConnected.value ? 'green' : 'gray'
})

const buttonText = computed(() => {
  if (connecting.value) return '连接中'
  return localConnected.value ? '断开' : '连接'
})

const valveConnectClass = computed(() => {
  const val = valveConnectState.value
  if (val === 'O') return 'green'
  if (val === 'C') return 'red'
  if (val === 'I') return 'blue'
  return 'gray'
})
const valveConnectText = computed(() => {
  const val = valveConnectState.value
  if (val === 'O') return '打开'
  if (val === 'C') return '关闭'
  if (val === 'I') return '转动中'
  return '未知'
})
const valveSprayClass = computed(() => {
  const val = valveSprayState.value
  if (val === 'O') return 'green'
  if (val === 'C') return 'red'
  if (val === 'I') return 'blue'
  return 'gray'
})
const valveSprayText = computed(() => {
  const val = valveSprayState.value
  if (val === 'O') return '打开'
  if (val === 'C') return '关闭'
  if (val === 'I') return '转动中'
  return '未知'
})

const connectionClass = (devId) => {
  const state = devStates[devId]
  if (!state || !state.lastSeen) return 'gray'
  return (Date.now() - state.lastSeen < 10000) ? 'green' : 'gray'
}
const connectionText = (devId) => {
  const state = devStates[devId]
  if (!state || !state.lastSeen) return '离线'
  return (Date.now() - state.lastSeen < 10000) ? '在线' : '离线'
}
const valveClass = (val) => {
  if (val === 'O') return 'green'
  if (val === 'C') return 'red'
  if (val === 'I') return 'blue'
  return 'gray'
}
const valveText = (val) => {
  if (val === 'O') return '打开'
  if (val === 'C') return '关闭'
  if (val === 'I') return '转动中'
  return '未知'
}

const startHeartbeat = () => {
  if (!isMultiDevice.value) return
  heartbeatInterval = setInterval(() => {
    const now = Date.now()
    devices.value.forEach(dev => {
      const state = devStates[dev.id]
      if (state && state.lastSeen && now - state.lastSeen > 10000) {
        // 超时，状态自动更新
      }
    })
  }, 5000)
}

const ensureDevices = async () => {
  if (deviceIds.value.length === 0) {
    router.push('/devices')
    return false
  }
  if (allDevices.value.length === 0) {
    try {
      await userStore.fetchDevices()
    } catch (error) {
      console.error('获取设备列表失败', error)
      router.push('/devices')
      return false
    }
  }
  if (devices.value.length === 0) {
    router.push('/devices')
    return false
  }
  return true
}

onMounted(async () => {
  const ok = await ensureDevices()
  if (!ok) return
  initMqtt()

  if (typeof window !== 'undefined') {
    window._debug = {
      devices: devices.value,
      devStates,
      mqttApi: mqttApi.value,
      env: MQTT_SERVER,
      valveConnectState,
      valveSprayState,
      localConnected,
      localMessages,
      connect,
      disconnect,
      sendCommand,
      goBackToDevices
    }
    console.log('✅ 调试对象已挂载到 window._debug')
  }

  startHeartbeat()
})

onUnmounted(() => {
  if (confirmTimeout) clearTimeout(confirmTimeout)
  if (heartbeatInterval) clearInterval(heartbeatInterval)
  mqttApi.value?.disconnect()
})
</script>

<style scoped>
/* 样式保持不变 */
.panel {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  font-family: Arial, sans-serif;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.back-button {
  padding: 6px 12px;
  background: #757575;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}
.back-button:hover {
  background: #616161;
}
.header-row h2 {
  margin: 0;
  font-size: 1.5em;
  color: #333;
  text-align: center;
  flex: 1;
}
.header-right {
  width: 80px;
}

.status-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.left-placeholder {
  flex: 1;
}
.device-info {
  flex: 0 1 auto;
  text-align: center;
  padding: 0 10px;
}
.device-name {
  font-weight: bold;
  color: #2196f3;
}
.conn-section {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}
.conn-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}
.led {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}
.led.green { background: #4caf50; box-shadow: 0 0 5px #4caf50; }
.led.red { background: #f44336; box-shadow: 0 0 5px #f44336; }
.led.blue { background: #2196f3; box-shadow: 0 0 5px #2196f3; }
.led.gray { background: #aaa; }

button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #2196f3;
  color: white;
  cursor: pointer;
  font-size: 16px;
}
button:hover { background: #1976d2; }
button:disabled { background: #90caf9; cursor: not-allowed; }

.multi-connect-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 20px 0;
}
.button-grid button { padding: 15px; }

.device-status {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 20px;
  padding: 15px;
  background: #e9e9e9;
  border-radius: 5px;
}
.status-item { text-align: center; }
.status-item .led { margin: 5px auto; }

.device-table-wrapper {
  margin-top: 20px;
  overflow-x: auto;
}
.device-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  background-color: #1e1e2f;
  color: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}
.device-table th {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 12px 8px;
  font-weight: bold;
}
.device-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #34495e;
  color: #ffffff;
}
.device-table tr:last-child td {
  border-bottom: none;
}
.status-led {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-led.green { background: #4caf50; }
.status-led.red { background: #f44336; }
.status-led.blue { background: #2196f3; }
.status-led.gray { background: #aaa; }

.feedback {
  margin-top: 20px;
  padding: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  max-height: 200px;
  overflow-y: auto;
  font-size: 12px;
}
.feedback div { padding: 2px 0; border-bottom: 1px solid #ccc; }

.no-device {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>