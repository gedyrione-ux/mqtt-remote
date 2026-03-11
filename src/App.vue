<template>
  <div id="app">
    <header v-if="isAuthenticated" class="app-header">
      <div class="user-info">
        <span>欢迎, {{ user?.username }}</span>
        <button @click="handleLogout" class="logout-btn">退出</button>
      </div>
    </header>
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth'

const router = useRouter()
const { user, token, logout } = useAuth()

const isAuthenticated = computed(() => !!token.value)

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  background: #2196f3;
  padding: 10px 20px;
  display: flex;
  justify-content: flex-end;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.user-info span {
  color: white;
}
.logout-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.logout-btn:hover {
  background: rgba(255,255,255,0.3);
}
</style>
