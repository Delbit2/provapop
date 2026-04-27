import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'
import { supabase } from '@/supabase'
import { api, setLogoutCallback } from '@/services/api'

interface User {
  id: string
  backend_id?: number | string
  nickname: string
  email?: string
  created_at?: string
  pontuacao?: number
  total_respondidas?: number
  total_acertos?: number
  ofensiva?: number
  recorde_ofensiva?: number
  data_ultima_partida?: string | null
}

let authListenerInitialized = false

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isVerifying = ref(false)
  const isFetchingProfile = ref(false)
  const authInitialized = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  function extractSafeUser(sbUser: any): User | null {
    if (!sbUser) return null

    let rawName =
      sbUser.user_metadata?.nickname ||
      sbUser.user_metadata?.nome ||
      sbUser.user_metadata?.name

    if (!rawName || String(rawName).trim() === '') {
      rawName = sbUser.email ? sbUser.email.split('@')[0] : 'Gamer Anônimo'
    }

    const safeName = String(rawName).trim()
    const finalName = safeName.charAt(0).toUpperCase() + safeName.slice(1)

    return {
      id: sbUser.id,
      email: sbUser.email,
      nickname: finalName,
      created_at: sbUser.created_at,
      pontuacao: 0,
      total_respondidas: 0,
      total_acertos: 0,
      ofensiva: 0,
      recorde_ofensiva: 0,
      data_ultima_partida: null,
    }
  }

  function mergeBackendProfile(baseUser: User | null, backendUser: any): User | null {
    if (!baseUser && !backendUser) return null

    const backendNickname =
      backendUser?.nickname ||
      backendUser?.nome ||
      backendUser?.name ||
      baseUser?.nickname ||
      'Gamer'

    return {
      id: baseUser?.id || String(backendUser?.id || ''),
      backend_id: backendUser?.id,
      nickname: backendNickname,
      email: backendUser?.email || baseUser?.email,
      created_at: baseUser?.created_at,
      pontuacao: Number(
        backendUser?.pontuacao ??
          backendUser?.pontuacao_total ??
          baseUser?.pontuacao ??
          0
      ),
      total_respondidas: Number(
        backendUser?.total_respondidas ??
          backendUser?.total_quizzes ??
          baseUser?.total_respondidas ??
          0
      ),
      total_acertos: Number(
        backendUser?.total_acertos ??
          backendUser?.correct_answers ??
          baseUser?.total_acertos ??
          0
      ),
      ofensiva: Number(
        backendUser?.ofensiva ??
          backendUser?.ofensiva_atual ??
          baseUser?.ofensiva ??
          0
      ),
      recorde_ofensiva: Number(
        backendUser?.recorde_ofensiva ??
          baseUser?.recorde_ofensiva ??
          0
      ),
      data_ultima_partida:
        backendUser?.data_ultima_partida ??
        backendUser?.data_ultima_missao_concluida ??
        baseUser?.data_ultima_partida ??
        null,
    }
  }

  async function getSupabaseUserOnly() {
    try {
      const {
        data: { user: sbUser },
      } = await supabase.auth.getUser()

      return extractSafeUser(sbUser)
    } catch {
      return null
    }
  }

  async function fetchUserProfile() {
    if (isFetchingProfile.value) return user.value

    isFetchingProfile.value = true

    try {
      const baseUser = await getSupabaseUserOnly()

      if (!baseUser) {
        user.value = null
        return null
      }

      try {
        const data = await api.auth.verify()

        if (data?.authenticated && data?.user) {
          user.value = mergeBackendProfile(baseUser, data.user)
          return user.value
        }
      } catch (backendErr) {
        console.warn(
          '[AUTH] Backend verify indisponível, usando perfil do Supabase:',
          backendErr
        )
      }

      user.value = baseUser
      return user.value
    } catch (err) {
      console.error('[AUTH] Erro ao buscar perfil completo:', err)
      return user.value
    } finally {
      isFetchingProfile.value = false
    }
  }

  async function initAuth() {
    if (authInitialized.value) return isAuthenticated.value
    return await verifyAuth(true)
  }

  async function forceLogout(redirect = true) {
    user.value = null
    error.value = null
    authInitialized.value = true

    try {
      await supabase.auth.signOut()
    } catch (err) {
      console.warn('[AUTH] Falha ao encerrar sessão no Supabase:', err)
    }

    if (redirect && router.currentRoute.value.path !== '/login') {
      await router.push('/login')
    }
  }

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const { data, error: sbError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (sbError) throw sbError

      user.value = extractSafeUser(data.user)
      await fetchUserProfile()
      authInitialized.value = true

      return data
    } catch (err: any) {
      error.value =
        err.message === 'Invalid login credentials'
          ? 'E-mail ou senha incorretos'
          : err.message || 'Erro ao fazer login'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(nickname: string, email: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const { data, error: sbError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { nickname },
        },
      })

      if (sbError) throw sbError

      user.value = extractSafeUser(data.user)

      if (data.session) {
        await fetchUserProfile()
      }

      authInitialized.value = true
      return data
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar conta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    try {
      try {
        await api.auth.logout()
      } catch (backendErr) {
        console.warn('[AUTH] Falha ao avisar logout para o backend:', backendErr)
      }

      await forceLogout(true)
    } catch (err: any) {
      error.value = err.message || 'Erro ao fazer logout'
    } finally {
      loading.value = false
    }
  }

  async function verifyAuth(markInitialized = false) {
    if (isVerifying.value) {
      return isAuthenticated.value
    }

    isVerifying.value = true

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session?.user) {
        user.value = null
        if (markInitialized) authInitialized.value = true
        return false
      }

      user.value = extractSafeUser(session.user)
      await fetchUserProfile()

      if (markInitialized) authInitialized.value = true
      return true
    } catch {
      user.value = null
      if (markInitialized) authInitialized.value = true
      return false
    } finally {
      isVerifying.value = false
    }
  }

  function initAuthListener() {
    if (authListenerInitialized) return
    authListenerInitialized = true

    setLogoutCallback(() => {
      forceLogout(true).catch((err) => {
        console.error('[AUTH] Falha no logout callback:', err)
      })
    })

    supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_OUT') {
        user.value = null
        authInitialized.value = true

        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }

        return
      }

      if (session?.user) {
        user.value = extractSafeUser(session.user)
        authInitialized.value = true

        fetchUserProfile().catch((err) => {
          console.error('[AUTH] Falha no onAuthStateChange:', err)
        })
      } else {
        user.value = null
        authInitialized.value = true
      }
    })
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isVerifying,
    authInitialized,
    login,
    register,
    logout,
    fetchUserProfile,
    verifyAuth,
    initAuth,
    forceLogout,
    initAuthListener,
  }
})
