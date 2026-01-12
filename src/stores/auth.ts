import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
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

  const isAuthenticated = computed(() => user.value !== null)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.auth.login(email, password)
      user.value = response.user
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
      await router.push('/login')
    } catch (err: any) {
      error.value = err.message || 'Erro ao fazer logout'
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      const response = await api.auth.me()
      user.value = response.user
      return response.user
    } catch (err) {
      user.value = null
      return null
    }
  }

  async function verifyAuth() {
    try {
      const response = await api.auth.verify()
      if (response.authenticated && response.user) {
        user.value = response.user
        return true
      }
      return false
    } catch (err) {
      user.value = null
      return false
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
  }
})