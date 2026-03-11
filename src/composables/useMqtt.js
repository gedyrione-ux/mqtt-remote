import { ref, onUnmounted } from 'vue'
import { WebSocketMqttClient, Mqtt } from '@ymjacky/mqtt5/browser'

export function useMqtt(options) {
  const connected = ref(false)
  const messages = ref([])
  let client = null

  const arrayBufferToHex = (buffer) => {
    let result = ''
    let bytes
    if (buffer instanceof Uint8Array) {
      bytes = buffer
    } else if (buffer instanceof ArrayBuffer) {
      bytes = new Uint8Array(buffer)
    } else if (Array.isArray(buffer)) {
      bytes = new Uint8Array(buffer)
    } else {
      return ''
    }
    for (let i = 0; i < bytes.length; i++) {
      const byte = bytes[i]
      let hex = byte.toString(16)
      if (hex.length === 1) hex = '0' + hex
      result += hex.toUpperCase()
      if (i < bytes.length - 1) result += ' '
    }
    return result
  }

  const connect = async () => {
    if (client) return

    try {
      // 创建 WebSocket MQTT 5.0 客户端实例
      client = new WebSocketMqttClient({
        url: new URL(options.server), // 确保 options.server 是完整的 WebSocket URL，如 'ws://...'
        clientId: options.clientId || 'web_' + Math.random().toString(16).substring(2, 8),
        username: options.username,
        password: options.password,
        clean: true,
        protocolVersion: Mqtt.ProtocolVersion.MQTT_V5,
        keepAlive: 60,
        logger: (msg, ...args) => console.log('[MQTT]', msg, ...args), // 可选，用于调试
      })

      // 设置消息监听（必须在 connect 之前）
      client.on('publish', (event) => {
        const packet = event.detail
        const payload = packet.payload // Uint8Array
        const topic = packet.topic

        // 处理收到的消息
        if (options.onMessage) {
          options.onMessage(topic, payload)
        }

        // 添加日志
        const hex = arrayBufferToHex(payload)
        if (options.onMessageAdd) {
          options.onMessageAdd(`📥 收到 [${topic}]: ${hex}`)
        }
      })

      // 建立连接
      await client.connect()

      connected.value = true
      console.log('MQTT 连接成功')
      if (options.onMessageAdd) {
        options.onMessageAdd('✅ 连接成功')
      }

      // 订阅主题（支持多主题数组）
      const topics = options.subscribeTopics || (options.subscribeTopic ? [options.subscribeTopic] : [])
      if (topics.length > 0) {
        await client.subscribe(topics, Mqtt.QoS.AT_LEAST_ONCE)
        if (options.onMessageAdd) {
          options.onMessageAdd(`📡 已订阅 ${topics.length} 个主题`)
        }
      }

      // 触发外部 onConnect 回调（与原来保持一致）
      if (options.onConnect) {
        options.onConnect()
      }

    } catch (error) {
      console.error('MQTT 连接错误:', error)
      if (options.onMessageAdd) {
        options.onMessageAdd(`❌ 错误: ${error.message}`)
      }
      connected.value = false
      client = null
    }
  }

  const disconnect = async () => {
    if (client) {
      try {
        await client.disconnect()
      } catch (error) {
        console.error('断开连接错误:', error)
      }
      client = null
      connected.value = false
      if (options.onMessageAdd) {
        options.onMessageAdd('🔌 已手动断开')
      }
    }
  }

  const publish = async (topic, message, qos = 1, properties = {}) => {
    if (!client || !connected.value) {
      if (options.onMessageAdd) {
        options.onMessageAdd('❌ 未连接，无法发送')
      }
      return false
    }

    try {
      // 转换 QoS 枚举
      const qosEnum = qos === 2 ? Mqtt.QoS.EXACTLY_ONCE :
                      qos === 1 ? Mqtt.QoS.AT_LEAST_ONCE :
                      Mqtt.QoS.AT_MOST_ONCE

      await client.publish(topic, message, {
        qos: qosEnum,
        properties: properties, // 直接透传 MQTT 5.0 属性
      })

      const hex = message instanceof Uint8Array ? arrayBufferToHex(message) : message
      if (options.onMessageAdd) {
        options.onMessageAdd(`📤 发送 [${topic}]: ${hex}`)
      }
      return true
    } catch (error) {
      if (options.onMessageAdd) {
        options.onMessageAdd(`❌ 发送失败: ${error.message}`)
      }
      return false
    }
  }

  const addMessage = (msg) => {
    const time = new Date().toLocaleTimeString()
    messages.value.unshift('[' + time + '] ' + msg)
    if (messages.value.length > 20) messages.value.pop()
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    messages,
    connect,
    disconnect,
    publish,
    addMessage,
  }
}