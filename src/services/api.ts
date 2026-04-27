import { supabase } from '@/supabase'

const rawApiBaseUrl =
  import.meta.env.VITE_API_URL || 'http://76.13.162.112:5000/api'

function normalizeApiBaseUrl(url: string) {
  const trimmed = url.replace(/\/+$/, '')
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`
}

const API_BASE_URL = normalizeApiBaseUrl(rawApiBaseUrl)

type QueryValue = string | number | boolean | undefined | null

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean
  timeoutMs?: number
  skipAutoLogoutOnAuthError?: boolean
}

interface ApiErrorPayload {
  error?: string
  message?: string
}

export interface AuthUser {
  id?: string | number
  email?: string
  nickname?: string
  pontuacao?: number
  role?: string
  [key: string]: any
}

export interface AuthResponse {
  message?: string
  user?: AuthUser
  authenticated?: boolean
}

export interface DailyQuestionResponse {
  status?: 'sucesso' | 'vazio'
  mensagem?: string
  partida_id?: number | null
  questoes?: any[]
}

export interface CheckAnswerResponse {
  is_correct: boolean
  correct_answer: string
  points: number
  total_score: number
  already_answered: boolean
  points_earned: boolean
  previous_result: boolean | null
  partida_id?: number | null
  limit_reached?: boolean
  limite_diario_atingido?: boolean
  missao_cumprida_agora?: boolean
  error?: string
}

let logoutCallback: (() => void) | null = null

export function setLogoutCallback(callback: () => void) {
  logoutCallback = callback
}

function buildUrl(endpoint: string) {
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  return `${API_BASE_URL}${normalizedEndpoint}`
}

export function buildQuery(params: Record<string, QueryValue>) {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  })

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

async function getSupabaseAccessToken() {
  const {
    data: { session },
    error,
  } = await supabase.auth.getSession()

  if (error) {
    console.error('[API] Erro ao obter sessão do Supabase:', error)
    return null
  }

  return session?.access_token || null
}

async function parseResponse(response: Response) {
  if (response.status === 204) return null

  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json().catch(() => null)
  }

  const text = await response.text().catch(() => '')
  return text || null
}

function extractErrorMessage(payload: unknown, response: Response) {
  if (payload && typeof payload === 'object') {
    const apiPayload = payload as ApiErrorPayload

    if (apiPayload.error) return apiPayload.error
    if (apiPayload.message) return apiPayload.message
  }

  switch (response.status) {
    case 400:
      return 'Requisição inválida.'
    case 401:
      return 'Não autorizado.'
    case 403:
      return 'Acesso negado.'
    case 404:
      return 'Recurso não encontrado.'
    case 409:
      return 'Conflito ao processar a requisição.'
    case 422:
      return 'Dados inválidos.'
    case 429:
      return 'Muitas tentativas. Tente novamente em instantes.'
    case 500:
      return 'Erro interno do servidor.'
    case 502:
    case 503:
    case 504:
      return 'Serviço temporariamente indisponível. Tente novamente.'
    default:
      return `Erro HTTP ${response.status}.`
  }
}

function shouldAddJsonContentType(body: BodyInit | null | undefined) {
  if (!body) return false
  if (body instanceof FormData) return false
  if (body instanceof URLSearchParams) return false
  if (body instanceof Blob) return false
  return true
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    requiresAuth = false,
    timeoutMs = 15000,
    skipAutoLogoutOnAuthError = false,
    ...fetchOptions
  } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  const headers = new Headers(fetchOptions.headers || {})
  headers.set('Accept', 'application/json')

  if (shouldAddJsonContentType(fetchOptions.body)) {
    headers.set('Content-Type', 'application/json')
  }

  if (requiresAuth) {
    const accessToken = await getSupabaseAccessToken()

    if (!accessToken) {
      if (!skipAutoLogoutOnAuthError) {
        logoutCallback?.()
      }

      clearTimeout(timeoutId)
      throw new Error('Sua sessão expirou. Faça login novamente.')
    }

    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  try {
    const response = await fetch(buildUrl(endpoint), {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    })

    const payload = await parseResponse(response)

    if (!response.ok) {
      const publicRoutes = ['/auth/login', '/auth/register']
      const isPublicRoute = publicRoutes.some((route) => endpoint.includes(route))
      const isProtectedAppRoute = requiresAuth && !isPublicRoute
      const errorMessage = extractErrorMessage(payload, response)

      if (
        (response.status === 401 || response.status === 403) &&
        isProtectedAppRoute &&
        !skipAutoLogoutOnAuthError
      ) {
        logoutCallback?.()

        if (response.status === 401) {
          throw new Error('Sessão expirada. Por favor, faça login novamente.')
        }

        throw new Error('Acesso negado. Você não tem permissão para esta ação.')
      }

      if (response.status === 401 && isPublicRoute) {
        throw new Error(errorMessage || 'Credenciais inválidas.')
      }

      throw new Error(errorMessage)
    }

    return payload as T
  } catch (err: any) {
    if (err?.name === 'AbortError') {
      throw new Error('A requisição demorou demais para responder. Tente novamente.')
    }

    if (err instanceof TypeError) {
      throw new Error(
        'Falha na comunicação com o servidor. Verifique sua conexão, a URL da API ou a configuração de CORS.'
      )
    }

    throw err
  } finally {
    clearTimeout(timeoutId)
  }
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<{ message: string; user: AuthUser }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        requiresAuth: false,
      }),

    register: (nickname: string, email: string, password: string) =>
      request<{ message: string; user: AuthUser }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ nickname, email, password }),
        requiresAuth: false,
      }),

    logout: () =>
      request<{ message: string }>('/auth/logout', {
        method: 'POST',
        requiresAuth: true,
        skipAutoLogoutOnAuthError: true,
      }),

    me: () =>
      request<{ user: AuthUser }>('/auth/me', {
        method: 'GET',
        requiresAuth: true,
      }),

    verify: () =>
      request<{ authenticated: boolean; user?: AuthUser }>('/auth/verify', {
        method: 'GET',
        requiresAuth: true,
        skipAutoLogoutOnAuthError: true,
      }),
  },

  daily: {
    getQuestions: () =>
      request<DailyQuestionResponse>('/questoes-do-dia', {
        method: 'GET',
        requiresAuth: true,
      }),
  },

  questions: {
    getAll: (category?: string) =>
      request<any[]>(`/questions${buildQuery({ category })}`, {
        method: 'GET',
        requiresAuth: false,
      }),

    getById: (id: number) =>
      request<any>(`/questions/${id}`, {
        method: 'GET',
        requiresAuth: false,
      }),

    getRandom: () =>
      request<any>('/questions/random', {
        method: 'GET',
        requiresAuth: false,
      }),

    checkAnswer: (questionId: number, selectedAnswer: string) =>
      request<CheckAnswerResponse>(`/questions/${questionId}/check`, {
        method: 'POST',
        body: JSON.stringify({ selected_answer: selectedAnswer }),
        requiresAuth: true,
      }),

    checkAnswerDetailed: (
      questionId: number,
      payload: {
        partida_id?: number | null
        alternativa_selecionada: string
        time_spent?: number
      }
    ) =>
      request<CheckAnswerResponse>(`/questions/${questionId}/check`, {
        method: 'POST',
        body: JSON.stringify(payload),
        requiresAuth: true,
      }),
  },

  users: {
    getStats: () =>
      request<{
        user_id: number
        total_quizzes: number
        correct_answers: number
        accuracy: number
        total_score: number
        total_points_calculated: number
      }>('/users/me/stats', {
        method: 'GET',
        requiresAuth: true,
      }),

    updateProfile: (data: { email?: string; password?: string }) =>
      request<{ message: string; user: AuthUser }>('/users/me/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
        requiresAuth: true,
      }),
  },

  ranking: {
    get: (period?: 'all' | 'week' | 'month') =>
      request<
        Array<{
          user_id: number
          nickname: string
          total_quizzes: number
          correct_answers: number
          accuracy: number
          position: number
          total_score: number
        }>
      >(
        `/ranking${buildQuery({
          period: period && period !== 'all' ? period : undefined,
        })}`,
        {
          method: 'GET',
          requiresAuth: false,
        }
      ),
  },
}

export { request, buildUrl }
