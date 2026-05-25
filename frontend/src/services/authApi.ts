import { apiClient } from '@/services/api'
import type { AuthUser, TokenResponse } from '@/types/auth'

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }),

  register: (email: string, password: string, full_name?: string) =>
    apiClient.post<TokenResponse>('/auth/register', { email, password, full_name }),

  refresh: (refresh_token: string) =>
    apiClient.post<TokenResponse>('/auth/refresh', { refresh_token }),

  me: () => apiClient.get<AuthUser>('/auth/me'),

  logout: () => apiClient.post('/auth/logout'),
}
