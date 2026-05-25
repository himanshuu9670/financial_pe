import { motion, AnimatePresence } from 'framer-motion'
import type { LedgerEntry } from '@/types/editSession'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { fieldValue, getFieldCoordinate } from '@/utils/workspace'

interface LivePreviewLayerProps {
  pageIndex: number
  scale: number
  entries: LedgerEntry[]
}

export function LivePreviewLayer({ pageIndex, scale, entries }: LivePreviewLayerProps) {
  const show = useWorkspaceStore((s) => s.showLivePreview)
  const lastPropagation = useWorkspaceStore((s) => s.lastPropagationAt)

  if (!show) return null

  const pageNum = pageIndex + 1

  return (
    <AnimatePresence>
      {entries
        .filter((e) => e.page === pageNum && (e.is_modified || e.propagation_affected))
        .map((entry) => {
          const fields = (['debit', 'credit', 'balance'] as const).filter((f) => {
            const c = getFieldCoordinate(entry, f)
            return c?.bbox && c.bbox.length >= 4
          })

          return fields.map((field) => {
            const coord = getFieldCoordinate(entry, field)!
            const rect = pdfBboxToViewport(coord.bbox, scale)
            const value = fieldValue(entry, field)
            if (!value) return null

            return (
              <motion.span
                key={`${entry.transaction_id}-${field}-${lastPropagation}`}
                initial={{ opacity: 0.4, y: -2 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute pointer-events-none font-mono text-cyan-300 whitespace-nowrap"
                style={{
                  left: rect.left,
                  top: rect.top,
                  fontSize: Math.max(9, (coord.font_size || 10) * scale * 0.85),
                  textShadow: '0 0 8px rgba(0,0,0,0.9), 0 1px 2px #000',
                }}
              >
                {value}
              </motion.span>
            )
          })
        })}
    </AnimatePresence>
  )
}
