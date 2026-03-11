import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import DeviceSelect from '../views/DeviceSelect.vue'
import RemoteController from '../components/RemoteController.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/devices',
    name: 'DeviceSelect',
    component: DeviceSelect,
    meta: { requiresAuth: true }
  },
  {
    path: '/remote',
    name: 'Remote',
    component: RemoteController,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/devices'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const { token } = useAuth()
  if (to.meta.requiresAuth && !token.value) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token.value) {
    next('/devices')
  } else {
    next()
  }
})

export default router