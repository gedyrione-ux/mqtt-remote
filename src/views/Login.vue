<template>
  <div class="auth-container">
    <div class="auth-box">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名或邮箱</label>
          <input v-model="form.usernameOrEmail" type="text" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p>
        还没有账号? <router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, loading, error } = useAuth()

const form = reactive({
  usernameOrEmail: '',
  password: ''
})

const handleLogin = async () => {
  try {
    await login(form.usernameOrEmail, form.password)
    router.push('/devices')
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
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
button:disabled { background: #90caf9; }
.error-message {
  color: #f44336;
  margin-bottom: 15px;
  text-align: center;
}
p { text-align: center; margin-top: 20px; }
a { color: #2196f3; }
</style>
