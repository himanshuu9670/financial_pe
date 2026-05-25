import type { LedgerEntry } from '@/types/editSession'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { getFieldCoordinate } from '@/utils/workspace'

interface CoordinateLayerProps {
  pageIndex: number
  scale: number
  entries: LedgerEntry[]
}

/** Debug: show field bbox outlines. */
export function CoordinateLayer({ pageIndex, scale, entries }: CoordinateLayerProps) {
  const show = useWorkspaceStore((s) => s.showDebugTools)
  if (!show) return null

  const pageNum = pageIndex + 1

  return (
    <>
      {entries
        .filter((e) => e.page === pageNum)
        .flatMap((entry) =>
          (['debit', 'credit', 'balance', 'description'] as const).map((field) => {
            const c = getFieldCoordinate(entry, field)
            if (!c?.bbox || c.bbox.length < 4) return null
            const rect = pdfBboxToViewport(c.bbox, scale)
            return (
              <div
                key={`${entry.transaction_id}-${field}-dbg`}
                className="absolute border border-dashed border-pink-400/50 pointer-events-none"
                style={{
                  left: rect.left,
                  top: rect.top,
                  width: rect.width,
                  height: rect.height,
                }}
                title={`${field} (${c.x}, ${c.y})`}
              />
            )
          }),
        )}
    </>
  )
}
