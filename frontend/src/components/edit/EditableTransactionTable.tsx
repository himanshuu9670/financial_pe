import { motion } from 'framer-motion'
import { AlertCircle, Check } from 'lucide-react'
import { useCallback, useState } from 'react'
import type { ChangeType, LedgerEntry, SessionStateResponse } from '@/types/editSession'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import { cn } from '@/utils/cn'

interface EditableTransactionTableProps {
  state: SessionStateResponse
  onUpdate: (transactionId: string, field: ChangeType, value: string | null) => void
  isUpdating: boolean
}

function fmt(val: string | number | null | undefined) {
  if (val == null || val === '') return ''
  const n = Number(val)
  if (Number.isNaN(n)) return String(val)
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function EditableCell({
  value,
  transactionId,
  field,
  onSave,
  disabled,
  className,
}: {
  value: string
  transactionId: string
  field: ChangeType
  onSave: (id: string, field: ChangeType, val: string | null) => void
  disabled: boolean
  className?: string
}) {
  const editingCell = useEditSessionStore((s) => s.editingCell)
  const setEditingCell = useEditSessionStore((s) => s.setEditingCell)
  const isEditing =
    editingCell?.transactionId === transactionId && editingCell?.field === field
  const [draft, setDraft] = useState(value)

  const startEdit = () => {
    setDraft(value.replace(/,/g, ''))
    setEditingCell({ transactionId, field })
  }

  const commit = () => {
    setEditingCell(null)
    const normalized = draft.trim() === '' ? null : draft.replace(/,/g, '')
    if (normalized !== value.replace(/,/g, '')) {
      onSave(transactionId, field, normalized)
    }
  }

  if (isEditing) {
    return (
      <input
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === 'Enter') commit()
          if (e.key === 'Escape') setEditingCell(null)
        }}
        disabled={disabled}
        className={cn(
          'w-full px-2 py-1 rounded bg-black/40 border border-cyan-500/50 text-sm font-mono outline-none',
          className,
        )}
      />
    )
  }

  return (
    <button
      type="button"
      onClick={startEdit}
      disabled={disabled}
      className={cn(
        'w-full text-left px-2 py-1 rounded hover:bg-white/5 font-mono text-xs transition-colors',
        className,
      )}
    >
      {value || '—'}
    </button>
  )
}

export function EditableTransactionTable({
  state,
  onUpdate,
  isUpdating,
}: EditableTransactionTableProps) {
  const rowClass = useCallback((entry: LedgerEntry) => {
    if (entry.is_modified) return 'bg-amber-500/10 border-l-2 border-l-amber-400'
    if (entry.propagation_affected) return 'bg-indigo-500/10 border-l-2 border-l-indigo-400'
    if (entry.validation_warnings.length) return 'bg-red-500/5 border-l-2 border-l-red-400/50'
    return 'border-l-2 border-l-transparent'
  }, [])

  return (
    <div className="overflow-auto flex-1">
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-[var(--color-surface-elevated)] z-10">
          <tr className="text-left text-zinc-500 text-xs uppercase tracking-wider">
            <th className="p-3 w-8" />
            <th className="p-3">Date</th>
            <th className="p-3">Description</th>
            <th className="p-3 text-right">Debit</th>
            <th className="p-3 text-right">Credit</th>
            <th className="p-3 text-right">Balance</th>
          </tr>
        </thead>
        <tbody>
          {state.entries.map((entry, i) => (
            <motion.tr
              key={entry.transaction_id}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: Math.min(i * 0.015, 0.4) }}
              className={cn('border-b border-white/5', rowClass(entry))}
            >
              <td className="p-2 text-center">
                {entry.is_modified && (
                  <span className="text-amber-400" title="Modified">
                    ●
                  </span>
                )}
                {entry.propagation_affected && !entry.is_modified && (
                  <span className="text-indigo-400" title="Propagated">
                    ↓
                  </span>
                )}
                {entry.validation_warnings.length > 0 && (
                  <AlertCircle className="w-3 h-3 text-red-400 inline" />
                )}
              </td>
              <td className="p-2 text-zinc-400 text-xs whitespace-nowrap">{entry.date ?? '—'}</td>
              <td className="p-2 max-w-[200px]">
                <span className="line-clamp-2 text-xs">{entry.description}</span>
              </td>
              <td className="p-2 text-right text-red-400/90">
                <EditableCell
                  value={fmt(entry.debit)}
                  transactionId={entry.transaction_id}
                  field="debit"
                  onSave={onUpdate}
                  disabled={isUpdating}
                  className="text-red-400/90"
                />
              </td>
              <td className="p-2 text-right text-emerald-400/90">
                <EditableCell
                  value={fmt(entry.credit)}
                  transactionId={entry.transaction_id}
                  field="credit"
                  onSave={onUpdate}
                  disabled={isUpdating}
                  className="text-emerald-400/90"
                />
              </td>
              <td className="p-2 text-right text-cyan-300/90">
                <EditableCell
                  value={fmt(entry.balance)}
                  transactionId={entry.transaction_id}
                  field="balance"
                  onSave={onUpdate}
                  disabled={isUpdating}
                  className="text-cyan-300/90"
                />
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>

      {state.validation_passed && (
        <div className="flex items-center gap-2 p-3 text-xs text-emerald-400">
          <Check className="w-4 h-4" />
          Ledger validation passed
        </div>
      )}
    </div>
  )
}
