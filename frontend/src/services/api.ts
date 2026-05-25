import axios from 'axios'
import type { HealthResponse, StatementListResponse, UploadResponse } from '@/types/api'
import type { DocumentExtraction } from '@/types/extraction'
import type { TransactionsResponse } from '@/types/transaction'
import { useAuthStore } from '@/store/useAuthStore'
import { authApi } from '@/services/authApi'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
})

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = useAuthStore.getState().refreshToken
      if (refresh) {
        try {
          const { data } = await authApi.refresh(refresh)
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return apiClient(original)
        } catch {
          useAuthStore.getState().logout()
        }
      }
    }
    return Promise.reject(error)
  },
)

export const healthApi = {
  check: () => apiClient.get<HealthResponse>('/health'),
}

export const statementsApi = {
  list: (skip = 0, limit = 50) =>
    apiClient.get<StatementListResponse>('/statements', { params: { skip, limit } }),
  get: (id: string) => apiClient.get(`/statements/${id}`),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<UploadResponse>('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  previewUrl: (id: string) => `${baseURL}/preview/${id}`,
  extract: (id: string, params?: { pages?: string; refresh?: boolean }) =>
    apiClient.get<DocumentExtraction>(`/statements/${id}/extract`, { params }),
  transactions: (id: string, params?: { refresh?: boolean; debug?: boolean }) =>
    apiClient.get<TransactionsResponse>(`/statements/${id}/transactions`, { params }),
}
