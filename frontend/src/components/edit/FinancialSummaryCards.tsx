import { motion } from 'framer-motion'
import { ArrowDownLeft, ArrowUpRight, Scale, Wallet } from 'lucide-react'
import type { SummarySchema } from '@/types/editSession'
import { cn } from '@/utils/cn'

function fmt(val: string | number | null | undefined) {
  if (val == null || val === '') return '—'
  const n = Number(val)
  if (Number.isNaN(n)) return String(val)
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function FinancialSummaryCards({
  summary,
  validationPassed,
}: {
  summary: SummarySchema
  validationPassed: boolean
}) {
  const cards = [
    {
      label: 'Opening',
      value: fmt(summary.opening_balance),
      icon: Wallet,
      accent: 'text-indigo-400',
    },
    {
      label: 'Total debit',
      value: fmt(summary.total_debit),
      icon: ArrowDownLeft,
      accent: 'text-red-400',
    },
    {
      label: 'Total credit',
      value: fmt(summary.total_credit),
      icon: ArrowUpRight,
      accent: 'text-emerald-400',
    },
    {
      label: 'Closing',
      value: fmt(summary.closing_balance),
      icon: Scale,
      accent: validationPassed ? 'text-cyan-400' : 'text-amber-400',
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((c, i) => (
        <motion.div
          key={c.label}
          layout
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="glass rounded-xl p-4 border border-white/10"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-zinc-500 uppercase tracking-wider">{c.label}</span>
            <c.icon className={cn('w-4 h-4', c.accent)} />
          </div>
          <p className={cn('text-lg font-semibold font-mono tracking-tight', c.accent)}>
            {c.value}
          </p>
        </motion.div>
      ))}
    </div>
  )
}
