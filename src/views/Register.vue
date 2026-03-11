<template>
  <div class="auth-container">
    <div class="auth-box">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" required />
        </div>
        <div class="form-group">
          <label>邮箱 (可选)</label>
          <input v-model="form.email" type="email" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" required minlength="6" />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="form.confirmPassword" type="password" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p>
        已有账号? <router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register, loading, error } = useAuth()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  try {
    await register(form.username, form.email || null, form.password)
    alert('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    console.error(err)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.auth-box {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
h2 { text-align: center; margin-bottom: 30px; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 5px; color: #333; }
input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
button:disabled { background: #a5d6a7; }
.error-message {
  color: #f44336;
  margin-bottom: 15px;
  text-align: center;
}
p { text-align: center; margin-top: 20px; }
a { color: #2196f3; }
</style>
