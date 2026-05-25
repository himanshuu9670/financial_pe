import { memo, useMemo, useRef, useState, useCallback, useEffect } from 'react'
import { motion } from 'framer-motion'
import type { ChangeType, LedgerEntry, SessionStateResponse } from '@/types/editSession'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { filterEntries, fmtAmount } from '@/utils/workspace'
import { cn } from '@/utils/cn'

const ROW_HEIGHT = 44
const OVERSCAN = 8

interface VirtualizedLedgerTableProps {
  state: SessionStateResponse
  onUpdate: (id: string, field: ChangeType, value: string | null) => void
  isUpdating: boolean
}

function LedgerRow({
  entry,
  isSelected,
  isHovered,
  isFlashing,
  onSelect,
  onHover,
  onUpdate,
  disabled,
}: {
  entry: LedgerEntry
  isSelected: boolean
  isHovered: boolean
  isFlashing: boolean
  onSelect: () => void
  onHover: (id: string | null) => void
  onUpdate: (id: string, field: ChangeType, val: string | null) => void
  disabled: boolean
}) {
  const editingCell = useEditSessionStore((s) => s.editingCell)
  const setEditingCell = useEditSessionStore((s) => s.setEditingCell)

  const renderCell = (field: ChangeType, val: string) => {
    const isEd =
      editingCell?.transactionId === entry.transaction_id && editingCell.field === field
    if (isEd) {
      return (
        <input
          autoFocus
          defaultValue={val.replace(/,/g, '')}
          className="w-full px-1 py-0.5 rounded bg-black/50 border border-cyan-500/50 text-xs font-mono"
          onBlur={(e) => {
            setEditingCell(null)
            const v = e.target.value.trim()
            onUpdate(entry.transaction_id, field, v === '' ? null : v)
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') (e.target as HTMLInputElement).blur()
            if (e.key === 'Escape') setEditingCell(null)
          }}
        />
      )
    }
    return (
      <button
        type="button"
        className="w-full text-left text-xs font-mono hover:text-cyan-300"
        onClick={() => setEditingCell({ transactionId: entry.transaction_id, field })}
        disabled={disabled}
      >
        {val || '—'}
      </button>
    )
  }

  return (
    <motion.tr
      layout
      className={cn(
        'border-b border-white/5 transition-colors',
        isSelected && 'bg-cyan-500/10',
        isHovered && !isSelected && 'bg-white/5',
        isFlashing && 'bg-amber-500/10',
        entry.is_modified && 'border-l-2 border-l-amber-400/60',
      )}
      style={{ height: ROW_HEIGHT }}
      onMouseEnter={() => onHover(entry.transaction_id)}
      onMouseLeave={() => onHover(null)}
      onClick={onSelect}
    >
      <td className="px-2 text-xs text-zinc-500">{entry.date ?? '—'}</td>
      <td className="px-2 text-xs truncate max-w-[140px]">{entry.description}</td>
      <td className="px-2 text-right text-rose-300/90">
        {renderCell('debit', fmtAmount(entry.debit))}
      </td>
      <td className="px-2 text-right text-emerald-300/90">
        {renderCell('credit', fmtAmount(entry.credit))}
      </td>
      <td className="px-2 text-right font-medium">
        {renderCell('balance', fmtAmount(entry.balance))}
      </td>
    </motion.tr>
  )
}

const MemoRow = memo(LedgerRow)

export function VirtualizedLedgerTable({
  state,
  onUpdate,
  isUpdating,
}: VirtualizedLedgerTableProps) {
  const [query, setQuery] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [viewportH, setViewportH] = useState(400)

  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const hoveredId = useTransactionStore((s) => s.hoveredTransactionId)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)
  const hoverTransaction = useTransactionStore((s) => s.hoverTransaction)
  const flashIds = useWorkspaceStore((s) => s.flashTransactionIds)

  const entries = useMemo(
    () => filterEntries(state.entries, query),
    [state.entries, query],
  )

  const totalHeight = entries.length * ROW_HEIGHT
  const start = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - OVERSCAN)
  const visibleCount = Math.ceil(viewportH / ROW_HEIGHT) + OVERSCAN * 2
  const end = Math.min(entries.length, start + visibleCount)
  const slice = entries.slice(start, end)
  const offsetY = start * ROW_HEIGHT

  const onScroll = useCallback(() => {
    if (scrollRef.current) setScrollTop(scrollRef.current.scrollTop)
  }, [])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setViewportH(el.clientHeight))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  return (
    <div className="flex flex-col h-full">
      <input
        type="search"
        placeholder="Filter transactions…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="mx-2 mb-2 px-3 py-1.5 rounded-lg bg-black/30 border border-white/10 text-sm"
      />
      <div
        ref={scrollRef}
        onScroll={onScroll}
        className="flex-1 overflow-auto mx-1"
        role="grid"
        aria-label="Transaction ledger"
      >
        <table className="w-full text-sm relative" style={{ height: totalHeight }}>
          <thead className="sticky top-0 z-10 bg-zinc-950/95 text-xs text-zinc-500">
            <tr>
              <th className="px-2 py-2 text-left">Date</th>
              <th className="px-2 py-2 text-left">Description</th>
              <th className="px-2 py-2 text-right">Debit</th>
              <th className="px-2 py-2 text-right">Credit</th>
              <th className="px-2 py-2 text-right">Balance</th>
            </tr>
          </thead>
          <tbody style={{ transform: `translateY(${offsetY}px)` }}>
            {slice.map((entry) => (
              <MemoRow
                key={entry.transaction_id}
                entry={entry}
                isSelected={selectedId === entry.transaction_id}
                isHovered={hoveredId === entry.transaction_id}
                isFlashing={flashIds.includes(entry.transaction_id)}
                onSelect={() => selectTransaction(entry.transaction_id)}
                onHover={hoverTransaction}
                onUpdate={onUpdate}
                disabled={isUpdating}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
