import { create } from 'zustand'
import type { DocumentExtraction, TextSpan } from '@/types/extraction'

interface PdfState {
  statementId: string | null
  fileUrl: string | null
  fileName: string | null
  currentPage: number
  totalPages: number
  zoom: number
  extraction: DocumentExtraction | null
  extractionLoading: boolean
  extractionError: string | null
  showOverlay: boolean
  selectedSpan: TextSpan | null
  hoveredSpanId: string | null

  setStatement: (id: string, fileName: string, fileUrl: string, totalPages?: number) => void
  clearStatement: () => void
  setCurrentPage: (page: number) => void
  setZoom: (zoom: number) => void
  setExtraction: (data: DocumentExtraction | null) => void
  setExtractionLoading: (loading: boolean) => void
  setExtractionError: (error: string | null) => void
  setShowOverlay: (show: boolean) => void
  setSelectedSpan: (span: TextSpan | null) => void
  setHoveredSpanId: (id: string | null) => void
}

export const usePdfStore = create<PdfState>((set) => ({
  statementId: null,
  fileUrl: null,
  fileName: null,
  currentPage: 1,
  totalPages: 0,
  zoom: 1,
  extraction: null,
  extractionLoading: false,
  extractionError: null,
  showOverlay: true,
  selectedSpan: null,
  hoveredSpanId: null,

  setStatement: (id, fileName, fileUrl, totalPages = 0) =>
    set({
      statementId: id,
      fileName,
      fileUrl,
      currentPage: 1,
      totalPages,
      extraction: null,
      extractionError: null,
      selectedSpan: null,
    }),
  clearStatement: () =>
    set({
      statementId: null,
      fileUrl: null,
      fileName: null,
      currentPage: 1,
      totalPages: 0,
      extraction: null,
      extractionError: null,
      selectedSpan: null,
    }),
  setCurrentPage: (page) => set({ currentPage: page }),
  setZoom: (zoom) => set({ zoom: Math.min(3, Math.max(0.5, zoom)) }),
  setExtraction: (data) =>
    set({
      extraction: data,
      totalPages: data?.total_pages ?? 0,
      extractionError: null,
    }),
  setExtractionLoading: (loading) => set({ extractionLoading: loading }),
  setExtractionError: (error) => set({ extractionError: error }),
  setShowOverlay: (show) => set({ showOverlay: show }),
  setSelectedSpan: (span) => set({ selectedSpan: span }),
  setHoveredSpanId: (id) => set({ hoveredSpanId: id }),
}))
