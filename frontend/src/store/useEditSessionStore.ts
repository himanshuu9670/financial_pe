import { create } from 'zustand'
import type { SessionStateResponse } from '@/types/editSession'

interface EditSessionState {
  sessionId: string | null
  statementId: string | null
  state: SessionStateResponse | null
  loading: boolean
  error: string | null
  debugMode: boolean
  editingCell: { transactionId: string; field: string } | null

  setSession: (sessionId: string, statementId: string) => void
  setState: (state: SessionStateResponse | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setDebugMode: (on: boolean) => void
  setEditingCell: (cell: { transactionId: string; field: string } | null) => void
  clear: () => void
}

export const useEditSessionStore = create<EditSessionState>((set) => ({
  sessionId: null,
  statementId: null,
  state: null,
  loading: false,
  error: null,
  debugMode: false,
  editingCell: null,

  setSession: (sessionId, statementId) => set({ sessionId, statementId, error: null }),
  setState: (state) => set({ state }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setDebugMode: (on) => set({ debugMode: on }),
  setEditingCell: (cell) => set({ editingCell: cell }),
  clear: () =>
    set({
      sessionId: null,
      statementId: null,
      state: null,
      error: null,
      editingCell: null,
    }),
}))
