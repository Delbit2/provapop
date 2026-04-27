import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/views/Home.vue'
import Quiz from '@/views/Quiz.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Profile from '@/views/Profile.vue'
import CategoryMenu from '@/views/CategoryMenu.vue'
import Ranking from '@/views/Ranking.vue'
import EsqueciSenha from '@/views/EsqueciSenha.vue'
import NovaSenha from '@/views/NovaSenha.vue'
import MissionCompleted from '@/views/MissionCompleted.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true, hideBottomNav: true },
    },
    {
      path: '/entrar',
      redirect: '/login',
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { requiresGuest: true, hideBottomNav: true },
    },
    {
      path: '/cadastro',
      redirect: '/register',
    },
    {
      path: '/esqueci-senha',
      name: 'forgot-password',
      component: EsqueciSenha,
      meta: { requiresGuest: true, hideBottomNav: true },
    },
    {
      path: '/nova-senha',
      name: 'reset-password',
      component: NovaSenha,
      meta: { hideBottomNav: true },
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true },
    },
    {
      path: '/provas',
      name: 'provas',
      component: CategoryMenu,
      meta: { requiresAuth: true },
    },
    {
      path: '/quiz/:prova',
      name: 'quiz',
      component: Quiz,
      meta: { requiresAuth: true, hideBottomNav: true },
      props: true,
    },
    {
      path: '/quiz',
      redirect: '/provas',
    },
    {
      path: '/missao-cumprida',
      name: 'mission-completed',
      component: MissionCompleted,
      meta: { requiresAuth: true, hideBottomNav: true },
    },
    {
      path: '/perfil',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true },
    },
    {
      path: '/ranking',
      name: 'ranking',
      component: Ranking,
      meta: { requiresAuth: true },
    },
    {
      path: '/jornada',
      name: 'jornada',
      component: () => import('@/views/jornada.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/ingresso',
      name: 'ingresso',
      component: () => import('@/views/Ticket.vue'),
      meta: { requiresAuth: true },
    },
    // 👇 NOVA ROTA DO E-BOOK ADICIONADA AQUI 👇
    {
      path: '/ebook',
      name: 'ebook',
      component: () => import('@/views/Ebook.vue'),
      meta: { requiresAuth: true, hideBottomNav: true },
    },
    // 👆 ===================================== 👆
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.authInitialized) {
    await authStore.initAuth()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return '/'
  }

  return true
})

export default router
