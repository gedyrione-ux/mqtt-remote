import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import DeviceSelect from '../views/DeviceSelect.vue'
import RemoteController from '../components/RemoteController.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import OperatorManage from '../views/admin/OperatorManage.vue'
import FleetManage from '../views/admin/FleetManage.vue'

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
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/fleet',
    children: [
      {
        path: 'fleet',
        name: 'FleetManage',
        component: FleetManage
      },
      {
        path: 'operators',
        name: 'OperatorManage',
        component: OperatorManage
      }
    ]
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
  const { token, user } = useAuth()
  
  if (to.meta.requiresAuth && !token.value) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token.value) {
    if (user.value?.is_admin) {
      next('/admin/fleet')
    } else {
      next('/devices')
    }
  } else if (to.meta.requiresAdmin && !user.value?.is_admin) {
    next('/devices')
  } else if (to.path === '/' && token.value) {
    if (user.value?.is_admin) {
      next('/admin/fleet')
    } else {
      next('/devices')
    }
  } else {
    next()
  }
})

export default router