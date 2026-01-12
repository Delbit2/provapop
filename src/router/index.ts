import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Quiz from '@/views/Quiz.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Profile from '@/views/Profile.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz',
      name: 'quiz',
      component: Quiz,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      const authenticated = await authStore.verifyAuth()
      if (!authenticated) {
        return next('/login')
      }
    }
  }
  
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return next('/')
  }
  
  next()
})

export default router
