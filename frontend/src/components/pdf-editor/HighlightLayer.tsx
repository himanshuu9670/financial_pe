import { motion, AnimatePresence } from 'framer-motion'
import type { LedgerEntry } from '@/types/editSession'
import { useTransactionStore } from '@/store/useTransactionStore'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { pdfBboxToViewport } from '@/utils/coordinates'

interface HighlightLayerProps {
  pageIndex: number
  scale: number
  entries: LedgerEntry[]
}

export function HighlightLayer({ pageIndex, scale, entries }: HighlightLayerProps) {
  const pageNum = pageIndex + 1
  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const flashIds = useWorkspaceStore((s) => s.flashTransactionIds)
  const show = useWorkspaceStore((s) => s.showHighlights)

  if (!show) return null

  const entry = entries.find(
    (e) => e.page === pageNum && (e.transaction_id === selectedId || flashIds.includes(e.transaction_id)),
  )
  if (!entry?.row_bbox || entry.row_bbox.length < 4) return null

  const rect = pdfBboxToViewport(entry.row_bbox as [number, number, number, number], scale)
  const isFlash = flashIds.includes(entry.transaction_id)

  return (
    <AnimatePresence>
      <motion.div
        key={entry.transaction_id + (isFlash ? '-flash' : '')}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute pointer-events-none rounded-md"
        style={{
          left: rect.left - 4,
          top: rect.top - 4,
          width: rect.width + 8,
          height: rect.height + 8,
          boxShadow: isFlash
            ? '0 0 28px rgba(251,191,36,0.55)'
            : '0 0 24px rgba(34,211,238,0.35)',
          border: isFlash ? '2px solid rgba(251,191,36,0.8)' : '2px solid rgba(34,211,238,0.5)',
        }}
      />
    </AnimatePresence>
  )
}
