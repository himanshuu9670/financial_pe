import { motion } from 'framer-motion'
import type { ChangeType, LedgerEntry } from '@/types/editSession'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { editableFields, getFieldCoordinate } from '@/utils/workspace'
import { cn } from '@/utils/cn'

interface SelectionLayerProps {
  pageIndex: number
  scale: number
  entries: LedgerEntry[]
  onFieldClick: (entry: LedgerEntry, field: ChangeType) => void
}

export function SelectionLayer({
  pageIndex,
  scale,
  entries,
  onFieldClick,
}: SelectionLayerProps) {
  const pageNum = pageIndex + 1
  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const hoveredId = useTransactionStore((s) => s.hoveredTransactionId)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)
  const hoverTransaction = useTransactionStore((s) => s.hoverTransaction)
  const pdfEditTarget = useWorkspaceStore((s) => s.pdfEditTarget)
  const flashIds = useWorkspaceStore((s) => s.flashTransactionIds)

  const pageEntries = entries.filter((e) => e.page === pageNum)

  return (
    <>
      {pageEntries.map((entry) => {
        const isSelected = selectedId === entry.transaction_id
        const isHovered = hoveredId === entry.transaction_id
        const isFlashing = flashIds.includes(entry.transaction_id)

        if (entry.row_bbox?.length >= 4) {
          const rowRect = pdfBboxToViewport(entry.row_bbox as [number, number, number, number], scale)
          return (
            <motion.div
              key={`row-${entry.transaction_id}`}
              layout
              className={cn(
                'absolute pointer-events-auto rounded-sm border-2 transition-colors',
                isSelected
                  ? 'border-cyan-400/90 bg-cyan-500/10'
                  : isHovered
                    ? 'border-emerald-400/70 bg-emerald-500/10'
                    : 'border-transparent',
                isFlashing && 'animate-pulse border-amber-400 bg-amber-400/15',
              )}
              style={{
                left: rowRect.left,
                top: rowRect.top,
                width: rowRect.width,
                height: Math.max(rowRect.height, 12),
              }}
              onMouseEnter={() => hoverTransaction(entry.transaction_id)}
              onMouseLeave={() => hoverTransaction(null)}
              onClick={() => selectTransaction(entry.transaction_id)}
            />
          )
        }
        return null
      })}

      {pageEntries.flatMap((entry) =>
        editableFields(entry).map((field) => {
          const coord = getFieldCoordinate(entry, field)
          if (!coord?.bbox || coord.bbox.length < 4) return null
          const rect = pdfBboxToViewport(coord.bbox, scale)
          const editing =
            pdfEditTarget?.transactionId === entry.transaction_id &&
            pdfEditTarget.field === field

          return (
            <button
              key={`${entry.transaction_id}-${field}`}
              type="button"
              className={cn(
                'absolute pointer-events-auto rounded border transition-all',
                'border-cyan-500/30 bg-cyan-400/5 hover:bg-cyan-400/20 hover:border-cyan-400/70',
                editing && 'ring-2 ring-cyan-400',
                entry.is_modified && field !== 'balance' && 'border-amber-400/50',
              )}
              style={{
                left: rect.left,
                top: rect.top,
                width: Math.max(rect.width, 24),
                height: Math.max(rect.height, 14),
              }}
              title={`Click to edit ${field}`}
              onClick={(e) => {
                e.stopPropagation()
                selectTransaction(entry.transaction_id)
                onFieldClick(entry, field)
              }}
            />
          )
        }),
      )}
    </>
  )
}
