const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://76.13.162.112:5000/api'

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean
}

// Função para deslogar o usuário quando não autorizado
let logoutCallback: (() => void) | null = null

export function setLogoutCallback(callback: () => void) {
  logoutCallback = callback
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { requiresAuth = false, ...fetchOptions } = options

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...fetchOptions.headers,
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
      credentials: 'include',
      mode: 'cors',
    })
  } catch (networkError) {
    // Erro de rede - não deslogar, apenas lançar erro
    throw new Error('Erro de conexão. Verifique sua internet e tente novamente.')
  }

  // Se receber 401 (Unauthorized) ou 403 (Forbidden), deslogar o usuário
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    const errorMessage = error.error || `HTTP error! status: ${response.status}`
    
    // Rotas públicas que não devem deslogar mesmo com 401/403
    const publicRoutes = ['/auth/login', '/auth/register', '/auth/verify']
    const isPublicRoute = publicRoutes.some(route => endpoint.includes(route))
    
    // Apenas deslogar em caso de 401/403 real e em rotas que requerem autenticação
    if ((response.status === 401 || response.status === 403) && !isPublicRoute && requiresAuth) {
      // Deslogar automaticamente quando não autorizado em rotas protegidas
      if (logoutCallback) {
        logoutCallback()
      }
      // Para erros de autenticação, usar mensagem mais específica
      if (response.status === 401) {
        throw new Error('Sessão expirada. Por favor, faça login novamente.')
      } else if (response.status === 403) {
        throw new Error('Acesso negado. Você não tem permissão para esta ação.')
      }
    }
    
    // Para rotas públicas com 401, apenas lançar erro sem deslogar
    if (response.status === 401 && isPublicRoute) {
      throw new Error(errorMessage || 'Credenciais inválidas')
    }
    
    throw new Error(errorMessage)
  }

  return response.json()
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<{ message: string; user: any }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        requiresAuth: false,
      }),

    register: (nickname: string, email: string, password: string) =>
      request<{ message: string; user: any }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ nickname, email, password }),
        requiresAuth: false,
      }),

    logout: () =>
      request<{ message: string }>('/auth/logout', {
        method: 'POST',
        requiresAuth: true,
      }),

    me: () =>
      request<{ user: any }>('/auth/me', {
        method: 'GET',
        requiresAuth: true,
      }),

    verify: () =>
      request<{ authenticated: boolean; user?: any }>('/auth/verify', {
        method: 'GET',
        requiresAuth: false,
      }),
  },

  questions: {
    getAll: (category?: string) => {
      const url = category ? `/questions?category=${encodeURIComponent(category)}` : '/questions'
      return request<any[]>(url, {
        method: 'GET',
        requiresAuth: false,
      })
    },

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
      request<{ 
        is_correct: boolean
        correct_answer: string
        points: number
        total_score: number
        already_answered: boolean
        points_earned: boolean
        previous_result: boolean | null
      }>(
        `/questions/${questionId}/check`,
        {
          method: 'POST',
          body: JSON.stringify({ selected_answer: selectedAnswer }),
          requiresAuth: true,
        }
      ),
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
      request<{ message: string; user: any }>('/users/me/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
        requiresAuth: true,
      }),
  },

  ranking: {
    get: (period?: 'all' | 'week' | 'month') => {
      const params = period && period !== 'all' ? `?period=${period}` : ''
      return request<
        Array<{
          user_id: number
          nickname: string
          total_quizzes: number
          correct_answers: number
          accuracy: number
          position: number
          total_score: number
        }>
      >(`/ranking${params}`, {
        method: 'GET',
        requiresAuth: false,
      })
    },
  },
}