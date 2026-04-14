import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Quiz from '@/views/Quiz.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Profile from '@/views/Profile.vue'
import CategoryMenu from '@/views/CategoryMenu.vue'
import Ranking from '@/views/Ranking.vue'
import EsqueciSenha from '@/views/EsqueciSenha.vue'
import NovaSenha from '@/views/NovaSenha.vue'
// 👇 Importamos a nova tela de Missão Cumprida aqui!
import MissionCompleted from '@/views/MissionCompleted.vue'
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
      path: '/esqueci-senha',
      name: 'forgot-password',
      component: EsqueciSenha,
      meta: { requiresGuest: true }
    },
    {
      path: '/nova-senha',
      name: 'reset-password',
      component: NovaSenha,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/categorias',
      name: 'categories',
      component: CategoryMenu,
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz/:category',
      name: 'quiz',
      component: Quiz,
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/quiz',
      redirect: '/categorias'
    },
    // 👇 Inserimos a Rota do Troféu logo após o Quiz!
    {
      path: '/missao-cumprida',
      name: 'mission-completed',
      component: MissionCompleted,
      meta: { requiresAuth: true }
    },
    {
      path: '/perfil',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }
    },
    {
      path: '/ranking',
      name: 'ranking',
      component: Ranking,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (authStore.isAuthenticated) {
      return next()
    }
    
    const authenticated = await authStore.verifyAuth()
    if (!authenticated) {
      return next('/login')
    }
    
    return next()
  }
  
  if (to.meta.requiresGuest) {
    if (authStore.isAuthenticated) {
      return next('/')
    }
    
    const authenticated = await authStore.verifyAuth()
    if (authenticated) {
      return next('/')
    }
    
    return next()
  }
  
  next()
})

export default router
