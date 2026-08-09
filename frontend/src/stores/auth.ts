import { defineStore } from 'pinia'
import apiClient from '@/api/client'

interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

interface MeResponse {
  username: string
  role: { code: string; display_name: string }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    username: null as string | null,
    role: null as string | null,
  }),
  actions: {
    async login(username: string, password: string): Promise<void> {
      const { data } = await apiClient.post<TokenResponse>('/auth/login', { username, password })
      this.accessToken = data.access_token
      const me = await apiClient.get<MeResponse>('/auth/me')
      this.username = me.data.username
      this.role = me.data.role.code
    },
    async refreshAccessToken(): Promise<string> {
      const { data } = await apiClient.post<TokenResponse>('/auth/refresh')
      this.accessToken = data.access_token
      return data.access_token
    },
    async logout(): Promise<void> {
      try {
        await apiClient.post('/auth/logout')
      } finally {
        this.accessToken = null
        this.username = null
        this.role = null
      }
    },
  },
})
