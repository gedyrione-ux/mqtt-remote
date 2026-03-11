import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data)
}

export const userApi = {
  getMe: () => api.get('/users/me'),
  getDevices: () => api.get('/devices'),
  getDevice: (deviceId) => api.get(`/devices/${deviceId}`),
  createDevice: (data) => api.post('/admin/devices', data),
  updateDevice: (deviceId, data) => api.put(`/admin/devices/${deviceId}`, data),
  deleteDevice: (deviceId) => api.delete(`/admin/devices/${deviceId}`),
  getAllDevices: (userId) => api.get('/admin/devices', { params: { user_id: userId } }),
  getAdminDevices: () => api.get('/admin/devices'),
  createAdminDevice: (data) => api.post('/admin/devices', data),
  updateAdminDevice: (deviceId, data) => api.put(`/admin/devices/${deviceId}`, data),
  deleteAdminDevice: (deviceId) => api.delete(`/admin/devices/${deviceId}`),
  getAdminUsers: () => api.get('/admin/users'),
  createAdminUser: (data) => api.post('/admin/users', data),
  deleteAdminUser: (userId) => api.delete(`/admin/users/${userId}`)
}

export default api
