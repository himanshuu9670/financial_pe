import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, ChevronDown, ChevronRight } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { ParsedTransaction } from '@/types/transaction'
import { useTransactionStore } from '@/store/useTransactionStore'
import { cn } from '@/utils/cn'

interface TransactionTableProps {
  onSelect?: (txn: ParsedTransaction) => void
}

function formatAmount(val: string | null) {
  if (val == null || val === '') return '—'
  const n = Number(val)
  if (Number.isNaN(n)) return val
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function TransactionTable({ onSelect }: TransactionTableProps) {
  const data = useTransactionStore((s) => s.data)
  const searchQuery = useTransactionStore((s) => s.searchQuery)
  const amountFilter = useTransactionStore((s) => s.amountFilter)
  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const hoveredId = useTransactionStore((s) => s.hoveredTransactionId)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)
  const hoverTransaction = useTransactionStore((s) => s.hoverTransaction)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const filtered = useMemo(() => {
    if (!data?.transactions) return []
    let list = data.transactions
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      list = list.filter(
        (t) =>
          t.description.toLowerCase().includes(q) ||
          (t.date?.toLowerCase().includes(q) ?? false),
      )
    }
    if (amountFilter === 'debit') list = list.filter((t) => t.debit != null && t.debit !== '')
    if (amountFilter === 'credit') list = list.filter((t) => t.credit != null && t.credit !== '')
    return list
  }, [data, searchQuery, amountFilter])

  if (!data) {
    return (
      <p className="text-sm text-zinc-500 py-12 text-center">Load a statement to view transactions.</p>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-wrap gap-2 p-3 border-b border-white/10">
        <input
          type="search"
          placeholder="Search description or date…"
          value={searchQuery}
          onChange={(e) => useTransactionStore.getState().setSearchQuery(e.target.value)}
          className="flex-1 min-w-[140px] px-3 py-1.5 rounded-lg bg-black/30 border border-white/10 text-sm focus:border-indigo-500/50 outline-none"
        />
        {(['all', 'debit', 'credit'] as const).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => useTransactionStore.getState().setAmountFilter(f)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium capitalize',
              amountFilter === f
                ? 'bg-indigo-600 text-white'
                : 'bg-white/5 text-zinc-400 hover:text-zinc-200',
            )}
          >
            {f}
          </button>
        ))}
      </div>

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
            <AnimatePresence mode="popLayout">
              {filtered.map((txn, i) => {
                const isSelected = selectedId === txn.transaction_id
                const isHovered = hoveredId === txn.transaction_id
                const expanded = expandedId === txn.transaction_id
                const hasWarnings = txn.validation_warnings.length > 0

                return (
                  <motion.tr
                    key={txn.transaction_id}
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: Math.min(i * 0.02, 0.5) }}
                    className={cn(
                      'border-b border-white/5 cursor-pointer transition-colors',
                      isSelected && 'bg-cyan-500/15',
                      isHovered && !isSelected && 'bg-emerald-500/10',
                      !isSelected && !isHovered && 'hover:bg-white/[0.03]',
                    )}
                    onMouseEnter={() => hoverTransaction(txn.transaction_id)}
                    onMouseLeave={() => hoverTransaction(null)}
                    onClick={() => {
                      selectTransaction(txn.transaction_id)
                      onSelect?.(txn)
                    }}
                  >
                    <td className="p-3 text-zinc-600">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          setExpandedId(expanded ? null : txn.transaction_id)
                        }}
                      >
                        {expanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </button>
                    </td>
                    <td className="p-3 whitespace-nowrap text-zinc-300">{txn.date ?? '—'}</td>
                    <td className="p-3 max-w-[220px]">
                      <span className="line-clamp-2">{txn.description}</span>
                      {hasWarnings && (
                        <span className="flex items-center gap-1 text-amber-500 text-xs mt-1">
                          <AlertCircle className="w-3 h-3" />
                          {txn.validation_warnings[0]}
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-right text-red-400/90 font-mono text-xs">
                      {formatAmount(txn.debit)}
                    </td>
                    <td className="p-3 text-right text-emerald-400/90 font-mono text-xs">
                      {formatAmount(txn.credit)}
                    </td>
                    <td className="p-3 text-right font-mono text-xs text-zinc-300">
                      {formatAmount(txn.balance)}
                    </td>
                  </motion.tr>
                )
              })}
            </AnimatePresence>
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="text-center py-8 text-zinc-500 text-sm">No transactions match filters.</p>
        )}
      </div>

      <div className="p-3 border-t border-white/10 grid grid-cols-3 gap-2 text-xs">
        <div>
          <p className="text-zinc-600">Debit total</p>
          <p className="font-mono text-red-400">{formatAmount(String(data.summary.total_debit))}</p>
        </div>
        <div>
          <p className="text-zinc-600">Credit total</p>
          <p className="font-mono text-emerald-400">
            {formatAmount(String(data.summary.total_credit))}
          </p>
        </div>
        <div>
          <p className="text-zinc-600">Closing</p>
          <p className="font-mono text-zinc-300">
            {formatAmount(
              data.summary.closing_balance != null ? String(data.summary.closing_balance) : null,
            )}
          </p>
        </div>
      </div>
    </div>
  )
}
