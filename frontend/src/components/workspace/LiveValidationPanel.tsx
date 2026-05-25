import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle2, FileOutput, Loader2, ScanLine } from 'lucide-react'
import type { SessionStateResponse } from '@/types/editSession'
import { cn } from '@/utils/cn'

interface LiveValidationPanelProps {
  state: SessionStateResponse
  isUpdating?: boolean
  exportReady?: boolean
}

export function LiveValidationPanel({
  state,
  isUpdating,
  exportReady = true,
}: LiveValidationPanelProps) {
  const passed = state.validation_passed
  const issues = state.validation_issues

  return (
    <div className="space-y-3 p-4">
      <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
        Live validation
      </h3>

      {isUpdating && (
        <div className="flex items-center gap-2 text-xs text-cyan-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Recalculating ledger…
        </div>
      )}

      <motion.div
        layout
        className={cn(
          'rounded-lg px-3 py-2 flex items-center gap-2 text-sm',
          passed ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300',
        )}
      >
        {passed ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
        {passed ? 'Ledger consistent' : 'Validation issues detected'}
      </motion.div>

      {issues.length > 0 && (
        <ul className="text-xs text-zinc-500 space-y-1 max-h-32 overflow-y-auto">
          {issues.map((issue, i) => (
            <li key={i}>• {issue}</li>
          ))}
        </ul>
      )}

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="rounded-lg bg-white/5 p-2">
          <p className="text-zinc-600">Modified</p>
          <p className="text-zinc-200 font-medium">{state.modified_count}</p>
        </div>
        <div className="rounded-lg bg-white/5 p-2">
          <p className="text-zinc-600">Rows</p>
          <p className="text-zinc-200 font-medium">{state.summary.transaction_count}</p>
        </div>
      </div>

      <div
        className={cn(
          'flex items-center gap-2 text-xs rounded-lg px-3 py-2 border',
          exportReady && passed
            ? 'border-indigo-500/30 bg-indigo-500/10 text-indigo-200'
            : 'border-zinc-700 text-zinc-500',
        )}
      >
        <FileOutput className="w-4 h-4" />
        {exportReady && passed ? 'Export ready' : 'Fix validation before export'}
      </div>

      <p className="text-[10px] text-zinc-600 flex items-center gap-1">
        <ScanLine className="w-3 h-3" />
        OCR confidence shown in AI Insights tab
      </p>
    </div>
  )
}
