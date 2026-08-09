import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  withCredentials: true,
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.set('Authorization', `Bearer ${auth.accessToken}`)
  }
  return config
})

let refreshPromise: Promise<string> | null = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
    const auth = useAuthStore()

    if (error.response?.status === 401 && original && !original._retried && original.url !== '/auth/refresh') {
      original._retried = true
      try {
        refreshPromise ??= auth.refreshAccessToken()
        const newToken = await refreshPromise
        refreshPromise = null
        original.headers.set('Authorization', `Bearer ${newToken}`)
        return apiClient(original)
      } catch (refreshError) {
        refreshPromise = null
        await auth.logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
