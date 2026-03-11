import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '../services/api'

export const useUserStore = defineStore('user', () => {
  const devices = ref([])
  const currentDevice = ref(null)

  const fetchDevices = async () => {
    try {
      const response = await userApi.getDevices()
      devices.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch devices:', error)
      throw error
    }
  }

  const setCurrentDevice = (device) => {
    currentDevice.value = device
  }

  const clearDevices = () => {
    devices.value = []
    currentDevice.value = null
  }

  return {
    devices,
    currentDevice,
    fetchDevices,
    setCurrentDevice,
    clearDevices
  }
})
