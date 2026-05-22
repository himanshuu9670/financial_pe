import axios from 'axios'
import type { ApplyEditsRequest, ApplyEditsResponse } from '@/types/export'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

const client = axios.create({ baseURL, timeout: 120_000 })

export const exportApi = {
  applyEdits: (payload: ApplyEditsRequest) =>
    client.post<ApplyEditsResponse>('/export/apply-edits', payload),

  previewOriginal: (statementId: string) => `${baseURL}/preview/${statementId}`,
  previewEdited: (statementId: string) => `${baseURL}/preview/${statementId}/edited`,
}
