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
      path: '/entrar',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/cadastro',
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
      path: '/perfil',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    // Se já está autenticado localmente, permitir acesso imediatamente
    // A verificação real será feita nas requisições autenticadas
    if (authStore.isAuthenticated) {
      return next()
    }
    
    // Se não parece autenticado, verificar com backend
    // Mas apenas se não estiver vindo de uma rota pública (evita verificação desnecessária)
    const authenticated = await authStore.verifyAuth()
    if (!authenticated) {
      // Se não estiver autenticado, redirecionar para login
      return next('/entrar')
    }
    
    // Se autenticado após verificação, permitir acesso
    return next()
  }
  
  if (to.meta.requiresGuest) {
    // Para rotas de guest, apenas verificar estado local
    // Não fazer verificação com backend para evitar delays
    if (authStore.isAuthenticated) {
      // Se parece autenticado, redirecionar para home
      return next('/')
    }
    // Se não está autenticado, permitir acesso à rota de guest
    return next()
  }
  
  // Para rotas sem meta, permitir acesso
  next()
})

export default router
