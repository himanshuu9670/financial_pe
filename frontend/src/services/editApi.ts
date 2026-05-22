import axios from 'axios'
import type { ChangeType, SessionStateResponse } from '@/types/editSession'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

const client = axios.create({ baseURL, timeout: 60_000 })

export const editApi = {
  startSession: (statementId: string) =>
    client.post<{ session_id: string; statement_id: string }>('/edit/start-session', {
      statement_id: statementId,
    }),

  getSessionState: (sessionId: string, debug = false) =>
    client.get<SessionStateResponse>('/edit/session-state', {
      params: { session_id: sessionId, debug },
    }),

  updateTransaction: (
    sessionId: string,
    transactionId: string,
    field: ChangeType,
    value: string | null,
  ) =>
    client.post<{ success: boolean; state: SessionStateResponse }>('/edit/update-transaction', {
      session_id: sessionId,
      transaction_id: transactionId,
      field,
      value,
    }),

  undo: (sessionId: string) =>
    client.post<SessionStateResponse>('/edit/undo', { session_id: sessionId }),

  redo: (sessionId: string) =>
    client.post<SessionStateResponse>('/edit/redo', { session_id: sessionId }),

  commit: (sessionId: string, notes?: string) =>
    client.post<SessionStateResponse>('/edit/commit', { session_id: sessionId, notes }),
}
