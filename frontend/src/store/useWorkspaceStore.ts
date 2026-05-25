import { create } from 'zustand'
import type { ChangeType } from '@/types/editSession'

export type LeftPanelTab = 'statements' | 'transactions' | 'history' | 'insights'
export type RightPanelTab = 'details' | 'summary' | 'validation' | 'typography' | 'ai'

export interface PdfEditTarget {
  transactionId: string
  field: ChangeType
  page: number
  bbox: [number, number, number, number]
  fontSize?: number
  font?: string
}

interface WorkspaceState {
  leftTab: LeftPanelTab
  rightTab: RightPanelTab
  pdfScale: number
  syncZoom: boolean
  syncScroll: boolean
  compareMode: boolean
  showLivePreview: boolean
  showHighlights: boolean
  showDebugTools: boolean
  showValidationOverlay: boolean
  showOcrHints: boolean
  pdfEditTarget: PdfEditTarget | null
  flashTransactionIds: string[]
  lastPropagationAt: number | null

  setLeftTab: (tab: LeftPanelTab) => void
  setRightTab: (tab: RightPanelTab) => void
  setPdfScale: (scale: number) => void
  setSyncZoom: (on: boolean) => void
  setSyncScroll: (on: boolean) => void
  setCompareMode: (on: boolean) => void
  setShowLivePreview: (on: boolean) => void
  setShowHighlights: (on: boolean) => void
  setShowDebugTools: (on: boolean) => void
  setPdfEditTarget: (target: PdfEditTarget | null) => void
  flashTransactions: (ids: string[]) => void
  markPropagation: () => void
  reset: () => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  leftTab: 'transactions',
  rightTab: 'summary',
  pdfScale: 1,
  syncZoom: true,
  syncScroll: true,
  compareMode: false,
  showLivePreview: true,
  showHighlights: true,
  showDebugTools: false,
  showValidationOverlay: true,
  showOcrHints: false,
  pdfEditTarget: null,
  flashTransactionIds: [],
  lastPropagationAt: null,

  setLeftTab: (tab) => set({ leftTab: tab }),
  setRightTab: (tab) => set({ rightTab: tab }),
  setPdfScale: (scale) => set({ pdfScale: Math.min(2.5, Math.max(0.5, scale)) }),
  setSyncZoom: (on) => set({ syncZoom: on }),
  setSyncScroll: (on) => set({ syncScroll: on }),
  setCompareMode: (on) => set({ compareMode: on }),
  setShowLivePreview: (on) => set({ showLivePreview: on }),
  setShowHighlights: (on) => set({ showHighlights: on }),
  setShowDebugTools: (on) => set({ showDebugTools: on }),
  setPdfEditTarget: (target) => set({ pdfEditTarget: target }),
  flashTransactions: (ids) =>
    set({ flashTransactionIds: ids, lastPropagationAt: Date.now() }),
  markPropagation: () => set({ lastPropagationAt: Date.now() }),
  reset: () =>
    set({
      pdfEditTarget: null,
      flashTransactionIds: [],
      compareMode: false,
    }),
}))
