import { useQuery } from '@tanstack/react-query'
import { FlaskConical } from 'lucide-react'
import { apiClient } from '@/services/api'
import { GlassCard } from '@/components/ui/GlassCard'

interface QaCheck {
  area: string
  status: string
  notes?: string | null
}

interface CeleryResilience {
  recovery_status: string
  retries_24h: number
  dead_letters_24h: number
  recoveries_24h: number
  queue_backlog: number
  statements_error: number
  exports: { queued: number; processing: number; failed: number }
  workers: { workers_online?: number; active_tasks?: number; reserved_tasks?: number }
}

interface QaDashboard {
  status: string
  checks: QaCheck[]
  failed_count: number
  warn_count: number
  generated_at: string
  docs: Record<string, string>
  celery?: CeleryResilience
  exports?: { queued: number; failed: number; processing?: number }
}

const statusColor: Record<string, string> = {
  pass: 'text-emerald-400',
  warn: 'text-amber-400',
  fail: 'text-rose-400',
}

export function AdminQaDashboardPanel() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-qa-dashboard'],
    queryFn: () => apiClient.get<QaDashboard>('/admin/qa-dashboard').then((r) => r.data),
    refetchInterval: 30000,
  })

  return (
    <GlassCard className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <FlaskConical className="w-5 h-5 text-violet-400" />
        <h2 className="font-semibold">QA dashboard</h2>
        {data && (
          <span
            className={`ml-auto text-xs uppercase tracking-wide ${
              data.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'
            }`}
          >
            {data.status}
          </span>
        )}
      </div>

      {isLoading && <p className="text-xs text-zinc-500">Loading QA checks…</p>}
      {error && (
        <p className="text-xs text-rose-400">QA dashboard unavailable (admin role required).</p>
      )}

      {data && (
        <>
          <p className="text-xs text-zinc-500 mb-3">
            Failed: {data.failed_count} · Warnings: {data.warn_count} · Updated{' '}
            {new Date(data.generated_at).toLocaleString()}
          </p>
          {data.celery && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs mb-3">
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Celery</span>
                <p className="text-violet-300 font-mono">{data.celery.recovery_status}</p>
              </div>
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Retries 24h</span>
                <p className="text-amber-300 font-mono">{data.celery.retries_24h}</p>
              </div>
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Dead letters 24h</span>
                <p className="text-rose-300 font-mono">{data.celery.dead_letters_24h}</p>
              </div>
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Queue backlog</span>
                <p className="text-cyan-300 font-mono">{data.celery.queue_backlog}</p>
              </div>
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Workers</span>
                <p className="text-zinc-200 font-mono">{data.celery.workers?.workers_online ?? 0}</p>
              </div>
              <div className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">Exports failed</span>
                <p className="text-rose-300 font-mono">{data.celery.exports.failed}</p>
              </div>
            </div>
          )}
          <ul className="space-y-1.5 max-h-56 overflow-auto">
            {data.checks.map((c) => (
              <li
                key={c.area}
                className="flex items-start gap-2 text-xs border-b border-white/5 pb-1.5"
              >
                <span className={statusColor[c.status] ?? 'text-zinc-400'}>{c.status}</span>
                <span className="text-zinc-300 font-mono flex-1">{c.area}</span>
                {c.notes && <span className="text-zinc-500 truncate max-w-[40%]">{c.notes}</span>}
              </li>
            ))}
          </ul>
          <p className="text-[10px] text-zinc-600 mt-3">
            Reports: {Object.values(data.docs).join(' · ')}
          </p>
        </>
      )}
    </GlassCard>
  )
}
