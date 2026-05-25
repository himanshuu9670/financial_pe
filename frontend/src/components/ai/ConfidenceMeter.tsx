import { motion } from 'framer-motion'
import type { ConfidenceBreakdown } from '@/types/ai'
import { cn } from '@/utils/cn'

interface ConfidenceMeterProps {
  confidence: ConfidenceBreakdown
  compact?: boolean
}

function Bar({ label, value }: { label: string; value?: number | null }) {
  if (value == null) return null
  const pct = Math.round(value * 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] text-zinc-500">
        <span>{label}</span>
        <span className="text-zinc-300">{pct}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </div>
  )
}

export function ConfidenceMeter({ confidence, compact }: ConfidenceMeterProps) {
  const overall = Math.round(confidence.overall * 100)
  const ringColor =
    overall >= 85 ? 'text-emerald-400' : overall >= 60 ? 'text-cyan-400' : 'text-amber-400'

  return (
    <div
      className={cn(
        'rounded-xl border border-white/10 bg-gradient-to-br from-zinc-900/80 to-indigo-950/40 p-3',
        compact && 'p-2',
      )}
    >
      <div className="flex items-center gap-3">
        <div
          className={cn(
            'relative flex items-center justify-center rounded-full border-2 border-current/30',
            ringColor,
            compact ? 'w-12 h-12 text-sm' : 'w-16 h-16 text-lg font-semibold',
          )}
        >
          <span className={ringColor}>{overall}%</span>
          <span className="absolute -inset-1 rounded-full bg-cyan-500/10 blur-md animate-pulse" />
        </div>
        <div>
          <p className="text-xs font-medium text-zinc-200">AI Extraction Confidence</p>
          <p className="text-[10px] text-zinc-500 mt-0.5">
            {confidence.factors.join(' · ') || 'Composite score'}
          </p>
        </div>
      </div>
      {!compact && (
        <div className="mt-3 space-y-2">
          <Bar label="OCR" value={confidence.ocr} />
          <Bar label="Layout" value={confidence.layout} />
          <Bar label="Financial" value={confidence.financial} />
          <Bar label="Semantic" value={confidence.semantic} />
        </div>
      )}
    </div>
  )
}
