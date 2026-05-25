import { apiClient } from '@/services/api'
import type { IntelligenceResponse } from '@/types/intelligence'

export const intelligenceApi = {
  analyze: (
    id: string,
    params?: { refresh?: boolean; force_ocr?: boolean },
  ) =>
    apiClient.get<IntelligenceResponse>(`/statements/${id}/intelligence`, {
      params: {
        refresh: params?.refresh,
        force_ocr: params?.force_ocr,
      },
    }),
}
