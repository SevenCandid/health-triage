import axios from 'axios'
import { authStore } from '@/stores/auth-store'

export const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// ── Request Interceptor ───────────────────────────────────────────────────────
// Attach the JWT access token to every outbound request if available.
apiClient.interceptors.request.use(
  (config) => {
    const token = authStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor ──────────────────────────────────────────────────────
// Handle global HTTP errors (401 unauthorised → clear auth state).
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.getState().clearAuth()
    }
    return Promise.reject(error)
  }
)
