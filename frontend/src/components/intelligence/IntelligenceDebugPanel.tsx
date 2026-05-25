import { motion } from 'framer-motion'
import {
  Brain,
  Columns3,
  Layers,
  ScanLine,
  Sparkles,
  TableProperties,
} from 'lucide-react'
import type { IntelligenceResponse } from '@/types/intelligence'
import { GlassCard } from '@/components/ui/GlassCard'
import { cn } from '@/utils/cn'

interface IntelligenceDebugPanelProps {
  data: IntelligenceResponse | undefined
  loading?: boolean
  onForceOcr?: () => void
  ocrLoading?: boolean
}

function ConfidenceBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-zinc-500">
        <span>{label}</span>
        <span className="text-zinc-300">{pct}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
        <motion.div
          className={cn(
            'h-full rounded-full',
            pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-orange-500',
          )}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

export function IntelligenceDebugPanel({
  data,
  loading,
  onForceOcr,
  ocrLoading,
}: IntelligenceDebugPanelProps) {
  if (loading) {
    return (
      <GlassCard className="p-6 flex items-center gap-3 text-zinc-400">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}
        >
          <Brain className="w-5 h-5 text-indigo-400" />
        </motion.div>
        <span className="text-sm">Running layout intelligence…</span>
      </GlassCard>
    )
  }

  if (!data) return null

  const mode = data.extraction_mode.toUpperCase()
  const isOcr = mode === 'OCR'

  return (
    <GlassCard className="p-5 space-y-4">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-sm">AI Document Intelligence</h3>
        </div>
        <span
          className={cn(
            'text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full',
            isOcr ? 'bg-orange-500/20 text-orange-300' : 'bg-emerald-500/20 text-emerald-300',
          )}
        >
          {mode}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-zinc-500">Bank</p>
          <p className="font-medium text-zinc-200 mt-0.5">
            {data.bank.replace(/_/g, ' ')}
          </p>
          <p className="text-zinc-600 mt-1">v{data.layout.bank.layout_version}</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-zinc-500">Transactions</p>
          <p className="font-medium text-zinc-200 mt-0.5">{data.transaction_count}</p>
        </div>
      </div>

      <ConfidenceBar value={data.layout_confidence} label="Layout confidence" />
      {data.ocr_confidence != null && (
        <ConfidenceBar value={data.ocr_confidence} label="OCR confidence" />
      )}
      <ConfidenceBar value={data.bank_confidence} label="Bank signature" />

      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded-lg bg-violet-500/10 p-2">
          <Columns3 className="w-4 h-4 mx-auto text-violet-400 mb-1" />
          <p className="text-zinc-400">{data.columns.length}</p>
          <p className="text-zinc-600">Columns</p>
        </div>
        <div className="rounded-lg bg-amber-500/10 p-2">
          <TableProperties className="w-4 h-4 mx-auto text-amber-400 mb-1" />
          <p className="text-zinc-400">{data.table_regions.length}</p>
          <p className="text-zinc-600">Tables</p>
        </div>
        <div className="rounded-lg bg-sky-500/10 p-2">
          <Layers className="w-4 h-4 mx-auto text-sky-400 mb-1" />
          <p className="text-zinc-400">{data.row_segments.length}</p>
          <p className="text-zinc-600">Rows</p>
        </div>
      </div>

      {data.layout.unknown_bank_adaptive && (
        <p className="text-xs text-amber-400/90 bg-amber-500/10 rounded-lg px-3 py-2">
          Unknown bank — adaptive column detection active
        </p>
      )}

      {data.warnings.length > 0 && (
        <ul className="text-xs text-zinc-500 space-y-1 max-h-24 overflow-y-auto">
          {data.warnings.slice(0, 6).map((w, i) => (
            <li key={i}>• {w}</li>
          ))}
        </ul>
      )}

      {onForceOcr && (
        <button
          type="button"
          onClick={onForceOcr}
          disabled={ocrLoading}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-medium bg-orange-500/15 text-orange-300 hover:bg-orange-500/25 transition-colors disabled:opacity-50"
        >
          <ScanLine className="w-4 h-4" />
          {ocrLoading ? 'Running OCR…' : 'Force OCR pipeline'}
        </button>
      )}
    </GlassCard>
  )
}
