import { AlertTriangle, ShieldAlert } from 'lucide-react'
import { motion } from 'framer-motion'
import type { AnomalyItem, FraudAssessment } from '@/types/ai'
import { cn } from '@/utils/cn'

interface AnomalyAlertsProps {
  anomalies: AnomalyItem[]
  fraud: FraudAssessment
  onSelect?: (transactionId: string) => void
}

const severityStyles = {
  high: 'border-rose-500/40 bg-rose-500/10 text-rose-200 shadow-[0_0_12px_rgba(244,63,94,0.25)]',
  medium: 'border-amber-500/30 bg-amber-500/10 text-amber-100',
  low: 'border-zinc-600/40 bg-zinc-800/50 text-zinc-300',
}

export function AnomalyAlerts({ anomalies, fraud, onSelect }: AnomalyAlertsProps) {
  const top = anomalies
    .filter((a) => a.severity === 'high' || a.severity === 'medium')
    .slice(0, 8)

  return (
    <div className="space-y-3">
      <div
        className={cn(
          'flex items-center gap-2 rounded-lg border px-3 py-2',
          fraud.risk_level === 'high' || fraud.risk_level === 'critical'
            ? 'border-rose-500/50 bg-rose-950/40'
            : 'border-indigo-500/30 bg-indigo-950/30',
        )}
      >
        <ShieldAlert className="w-4 h-4 text-indigo-300 shrink-0" />
        <div className="min-w-0">
          <p className="text-xs font-medium text-zinc-100">
            Fraud risk: {Math.round(fraud.risk_score * 100)}% ({fraud.risk_level})
          </p>
          {fraud.flags.map((f) => (
            <p key={f} className="text-[10px] text-zinc-500 truncate">
              {f}
            </p>
          ))}
        </div>
      </div>

      {top.length === 0 ? (
        <p className="text-xs text-zinc-500">No high-severity anomalies detected.</p>
      ) : (
        <ul className="space-y-2">
          {top.map((a) => (
            <motion.li
              key={`${a.transaction_id}-${a.anomaly_type}`}
              layout
              className={cn(
                'rounded-lg border px-2 py-1.5 text-[11px] cursor-pointer transition-colors',
                severityStyles[a.severity as keyof typeof severityStyles] ?? severityStyles.low,
              )}
              onClick={() => onSelect?.(a.transaction_id)}
            >
              <div className="flex items-start gap-1.5">
                <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium">{a.anomaly_type.replace(/_/g, ' ')}</p>
                  <p className="opacity-80">{a.message}</p>
                </div>
              </div>
            </motion.li>
          ))}
        </ul>
      )}
    </div>
  )
}
