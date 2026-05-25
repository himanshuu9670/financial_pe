import { apiClient } from '@/services/api'

export interface ExportJob {
  id: string
  statement_id: string
  status: string
  export_name: string | null
  replacements_applied: number
  validation_passed: boolean | null
  error_message: string | null
  download_url: string | null
  created_at: string
  completed_at: string | null
}

export const exportQueueApi = {
  queue: (statement_id: string, session_id?: string) =>
    apiClient.post<ExportJob>('/exports/queue', { statement_id, session_id }),

  getJob: (job_id: string) => apiClient.get<ExportJob>(`/exports/jobs/${job_id}`),

  listForStatement: (statement_id: string) =>
    apiClient.get<{ jobs: ExportJob[]; total: number }>(`/exports/statement/${statement_id}`),
}
