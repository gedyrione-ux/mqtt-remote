<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
      <h2>飞瀑环保调度台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link
          to="/admin/fleet"
          class="nav-link"
          active-class="active"
        >
          <span>🚛</span> 装备车辆库
        </router-link>
        <router-link
          to="/admin/operators"
          class="nav-link"
          active-class="active"
        >
          <span>👥</span> 操作员管理
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-btn">
          退出登录
        </button>
      </div>
    </aside>
    <main class="content">
      <div class="content-header">
        <div class="user-info">
          <span>管理员: {{ user?.username }}</span>
        </div>
      </div>
      <div class="content-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { user, logout } = useAuth()

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: #1a1a1a;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
  display: flex;
  flex-direction: column;
  border-right: 2px solid #34495e;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #34495e;
}

.sidebar-header h2 {
  color: #ecf0f1;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  color: #bdc3c7;
  text-decoration: none;
  font-size: 15px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background: rgba(52, 73, 94, 0.5);
  color: #fff;
}

.nav-link.active {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border-left-color: #3498db;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #34495e;
}

.logout-btn {
  width: 100%;
  padding: 12px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #c0392b;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.content-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: flex-end;
}

.user-info {
  color: #333;
  font-size: 14px;
}

.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
