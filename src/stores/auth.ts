import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, setLogoutCallback } from '@/services/api'
import router from '@/router'

interface User {
  id: number
  nickname: string
  email?: string
  created_at?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isVerifying = ref(false)
  const lastVerification = ref<number>(0)
  const VERIFICATION_CACHE_TIME = 30000 // 30 segundos

  const isAuthenticated = computed(() => user.value !== null)

  // Função para deslogar e limpar estado
  async function forceLogout() {
    user.value = null
    error.value = null
    lastVerification.value = 0
    // Não chamar a API de logout aqui para evitar loop infinito
    // Apenas limpar o estado local e redirecionar
    if (router.currentRoute.value.path !== '/entrar') {
      await router.push('/entrar')
    }
  }

  // Registrar callback para ser chamado quando API detectar 401/403
  setLogoutCallback(forceLogout)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.auth.login(email, password)
      user.value = response.user
      lastVerification.value = Date.now()
      
      // Aguardar um pouco para dar tempo da sincronização no backend acontecer
      // (a sincronização roda em background, então não bloqueia)
      setTimeout(() => {
        // Forçar recarregamento de questões após login
        // Isso será feito automaticamente quando o usuário acessar o quiz
        console.log('[AUTH] Login successful, questions will be synced automatically')
      }, 1000)
      
      await router.push('/')
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao fazer login'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(nickname: string, email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.auth.register(nickname, email, password)
      user.value = response.user
      lastVerification.value = Date.now()
      await router.push('/')
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar conta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await api.auth.logout()
      user.value = null
      await router.push('/entrar')
    } catch (err: any) {
      error.value = err.message || 'Erro ao fazer logout'
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      const response = await api.auth.me()
      if (response.user) {
        user.value = response.user
        lastVerification.value = Date.now()
        return response.user
      }
      // Se não houver usuário na resposta, deslogar
      await forceLogout()
      return null
    } catch (err: any) {
      // Se for erro 401/403, já foi tratado pelo api.ts
      // Apenas limpar o estado local
      user.value = null
      lastVerification.value = 0
      return null
    }
  }

  async function verifyAuth(force = false) {
    // Se já está verificando, aguardar
    if (isVerifying.value) {
      // Aguardar até que a verificação atual termine
      while (isVerifying.value) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      return user.value !== null
    }

    // Se já verificou recentemente e não for forçado, usar cache
    const now = Date.now()
    if (!force && user.value && (now - lastVerification.value) < VERIFICATION_CACHE_TIME) {
      return true
    }

    isVerifying.value = true
    try {
      const response = await api.auth.verify()
      if (response.authenticated && response.user) {
        user.value = response.user
        lastVerification.value = now
        return true
      }
      // Se não estiver autenticado, limpar estado apenas se já havia um usuário
      // Isso evita limpar estado em rotas públicas quando não há usuário
      if (!response.authenticated && user.value) {
        // Só limpar se havia um usuário antes (sessão expirou)
        user.value = null
        lastVerification.value = 0
      }
      return false
    } catch (err: any) {
      // Se houver erro de rede, manter o estado atual se já estiver autenticado
      // Apenas limpar se realmente não houver usuário
      if (!user.value) {
        lastVerification.value = 0
        return false
      }
      // Se já está autenticado e houve erro de rede, assumir que ainda está autenticado
      // A verificação real será feita na próxima requisição autenticada
      return true
    } finally {
      isVerifying.value = false
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    verifyAuth,
    forceLogout,
  }
})