import { motion } from 'framer-motion'
import type { SessionStateResponse } from '@/types/editSession'
import { fmtAmount } from '@/utils/workspace'

interface LiveSummaryDashboardProps {
  state: SessionStateResponse
}

export function LiveSummaryDashboard({ state }: LiveSummaryDashboardProps) {
  const s = state.summary

  const cards = [
    { label: 'Opening', value: fmtAmount(s.opening_balance), color: 'text-zinc-200' },
    { label: 'Closing', value: fmtAmount(s.closing_balance), color: 'text-cyan-300' },
    { label: 'Total debit', value: fmtAmount(s.total_debit), color: 'text-rose-300' },
    { label: 'Total credit', value: fmtAmount(s.total_credit), color: 'text-emerald-300' },
    { label: 'Edits', value: String(state.modified_count), color: 'text-amber-300' },
    {
      label: 'Status',
      value: state.validation_passed ? 'Valid' : 'Issues',
      color: state.validation_passed ? 'text-emerald-400' : 'text-red-400',
    },
  ]

  return (
    <div className="p-4 grid grid-cols-2 gap-2">
      {cards.map((c) => (
        <motion.div
          key={c.label}
          layout
          className="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
        >
          <p className="text-[10px] text-zinc-500 uppercase tracking-wide">{c.label}</p>
          <p className={`text-sm font-semibold mt-0.5 ${c.color}`}>{c.value || '—'}</p>
        </motion.div>
      ))}
    </div>
  )
}
