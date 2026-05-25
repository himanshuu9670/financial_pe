import { motion } from 'framer-motion'
import { Clock, GitBranch } from 'lucide-react'
import type { SessionStateResponse } from '@/types/editSession'
import { cn } from '@/utils/cn'

interface EditHistoryTimelineProps {
  state: SessionStateResponse
}

export function EditHistoryTimeline({ state }: EditHistoryTimelineProps) {
  const timeline = state.edit_timeline ?? []
  const traces = state.propagation_trace

  return (
    <div className="p-3 space-y-4 h-full overflow-y-auto">
      <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
        <Clock className="w-4 h-4" />
        Edit timeline
      </h3>

      {timeline.length === 0 && traces.length === 0 && (
        <p className="text-xs text-zinc-600">No edits yet — click PDF amounts or table cells.</p>
      )}

      <ul className="space-y-2">
        {[...timeline].reverse().map((ev, i) => (
          <motion.li
            key={ev.operation_id + i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-xs rounded-lg px-3 py-2 bg-white/5 border border-white/10"
          >
            <p className="text-zinc-200">{ev.description}</p>
            <p className="text-zinc-600 mt-0.5">
              {new Date(ev.timestamp).toLocaleTimeString()}
            </p>
          </motion.li>
        ))}
      </ul>

      {traces.length > 0 && (
        <>
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2 mt-4">
            <GitBranch className="w-4 h-4" />
            Last propagation
          </h3>
          <ul className="space-y-1.5">
            {traces.slice(0, 12).map((t, i) => (
              <li
                key={`${t.transaction_id}-${i}`}
                className={cn(
                  'text-[11px] rounded px-2 py-1.5',
                  'bg-amber-500/10 border border-amber-500/20 text-amber-200/90',
                )}
              >
                {t.field}: {t.old_value ?? '—'} → {t.new_value ?? '—'}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
