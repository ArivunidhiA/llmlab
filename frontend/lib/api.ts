import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  signup: (email: string, password: string, first_name?: string, last_name?: string) =>
    apiClient.post('/api/auth/signup', { email, password, first_name, last_name }),
  
  login: (email: string, password: string) =>
    apiClient.post('/api/auth/login', { email, password }),
  
  logout: () =>
    apiClient.post('/api/auth/logout'),
  
  getMe: () =>
    apiClient.get('/api/auth/me'),
}

export const events = {
  track: (provider: string, model: string, input_tokens: number, output_tokens: number, duration_ms?: number) =>
    apiClient.post('/api/events/track', { provider, model, input_tokens, output_tokens, duration_ms }),
  
  list: (limit?: number, offset?: number) =>
    apiClient.get('/api/events', { params: { limit, offset } }),
}

export const costs = {
  summary: () =>
    apiClient.get('/api/costs/summary'),
  
  recommendations: () =>
    apiClient.get('/api/recommendations'),
}

export const budgets = {
  create: (monthly_limit: number, alert_channel?: string) =>
    apiClient.post('/api/budgets', { monthly_limit, alert_channel }),
  
  list: () =>
    apiClient.get('/api/budgets'),
  
  update: (budgetId: string, data: any) =>
    apiClient.put(`/api/budgets/${budgetId}`, data),
  
  delete: (budgetId: string) =>
    apiClient.delete(`/api/budgets/${budgetId}`),
}
