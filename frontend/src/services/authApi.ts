import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加token
api.interceptors.request.use((config) => {
  const authStorage = localStorage.getItem('auth-storage')
  if (authStorage) {
    try {
      const { state } = JSON.parse(authStorage)
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`
      }
    } catch {
      // ignore parse errors
    }
  }
  return config
})

// 响应拦截器 - 处理401错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface RegisterRequest {
  email: string
  password: string
  display_name?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    display_name: string | null
    onboarding_completed: boolean
    created_at: string
    last_login: string | null
  }
}

export interface UserResponse {
  id: number
  email: string
  display_name: string | null
  onboarding_completed: boolean
  created_at: string
  last_login: string | null
}

// 注册
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await api.post('/auth/register', data)
  return response.data
}

// 登录
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await api.post('/auth/login', data)
  return response.data
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await api.get('/auth/me')
  return response.data
}

// 检查邮箱是否已注册
export const checkEmail = async (email: string): Promise<{ exists: boolean }> => {
  const response = await api.get('/auth/check-email', { params: { email } })
  return response.data
}
