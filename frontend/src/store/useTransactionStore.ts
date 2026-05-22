import { create } from 'zustand'
import type { ParsedTransaction, TransactionsResponse } from '@/types/transaction'

export type AmountFilter = 'all' | 'debit' | 'credit'

interface TransactionState {
  data: TransactionsResponse | null
  loading: boolean
  error: string | null
  selectedTransactionId: string | null
  hoveredTransactionId: string | null
  searchQuery: string
  amountFilter: AmountFilter
  debugMode: boolean
  showRowBboxes: boolean
  showColumnGuides: boolean
  showSpanOverlay: boolean

  setData: (data: TransactionsResponse | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  selectTransaction: (id: string | null) => void
  hoverTransaction: (id: string | null) => void
  setSearchQuery: (q: string) => void
  setAmountFilter: (f: AmountFilter) => void
  setDebugMode: (on: boolean) => void
  setShowRowBboxes: (on: boolean) => void
  setShowColumnGuides: (on: boolean) => void
  setShowSpanOverlay: (on: boolean) => void
  getSelectedTransaction: () => ParsedTransaction | undefined
}

export const useTransactionStore = create<TransactionState>((set, get) => ({
  data: null,
  loading: false,
  error: null,
  selectedTransactionId: null,
  hoveredTransactionId: null,
  searchQuery: '',
  amountFilter: 'all',
  debugMode: false,
  showRowBboxes: true,
  showColumnGuides: false,
  showSpanOverlay: false,

  setData: (data) => set({ data, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  selectTransaction: (id) => set({ selectedTransactionId: id }),
  hoverTransaction: (id) => set({ hoveredTransactionId: id }),
  setSearchQuery: (q) => set({ searchQuery: q }),
  setAmountFilter: (f) => set({ amountFilter: f }),
  setDebugMode: (on) => set({ debugMode: on }),
  setShowRowBboxes: (on) => set({ showRowBboxes: on }),
  setShowColumnGuides: (on) => set({ showColumnGuides: on }),
  setShowSpanOverlay: (on) => set({ showSpanOverlay: on }),
  getSelectedTransaction: () => {
    const { data, selectedTransactionId } = get()
    return data?.transactions.find((t) => t.transaction_id === selectedTransactionId)
  },
}))
