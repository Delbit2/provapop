const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { requiresAuth = false, ...fetchOptions } = options

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  }

  if (requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
    credentials: 'include',
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(error.error || `HTTP error! status: ${response.status}`)
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
    getAll: () =>
      request<any[]>('/questions', {
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
      request<{ is_correct: boolean; correct_answer: string }>(
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
    get: () =>
      request<
        Array<{
          user_id: number
          nickname: string
          total_quizzes: number
          correct_answers: number
          accuracy: number
          position: number
        }>
      >('/ranking', {
        method: 'GET',
        requiresAuth: false,
      }),
  },
}