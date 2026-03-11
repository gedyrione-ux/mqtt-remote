import { ref, reactive } from 'vue'
import { authApi } from '../services/api'
import { useUserStore } from '../stores/user'

const user = ref(null)
const token = ref(localStorage.getItem('access_token'))

if (token.value) {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    user.value = JSON.parse(savedUser)
  }
}

export function useAuth() {
  const userStore = useUserStore()
  const loading = ref(false)
  const error = ref(null)

  const login = async (usernameOrEmail, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login({ username_or_email: usernameOrEmail, password })
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('access_token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (username, email, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.register({ username, email, password })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '注册失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    userStore.clearDevices()
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout
  }
}
