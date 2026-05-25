import { Activity, Database, HardDrive, Server, Sparkles } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { GlassCard } from '@/components/ui/GlassCard'
import { cn } from '@/utils/cn'

interface MonitoringOverview {
  status: string
  health: {
    checks?: Record<string, boolean>
    celery?: { workers_online?: number; active_tasks?: number }
    ocr?: { available?: boolean }
  }
  workers: {
    workers_online?: number
    active_tasks?: number
    reserved_tasks?: number
    queues?: Record<string, number>
  }
  cache: {
    enabled?: boolean
    aggregate_hit_ratio?: number
    cache?: {
      hit_rates?: Record<string, number>
      redis_latency_ms?: { avg?: number; p95?: number }
    }
    redis?: { connected?: boolean; used_memory_human?: string; evicted_keys?: number }
  }
  exports: { queued?: number; failed?: number; queue_depth?: number }
}

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={cn(
        'inline-block w-2 h-2 rounded-full',
        ok ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]' : 'bg-rose-500',
      )}
    />
  )
}

export function AdminMonitoringPanel() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-monitoring'],
    queryFn: () => apiClient.get<MonitoringOverview>('/admin/monitoring').then((r) => r.data),
    refetchInterval: 10000,
    staleTime: 5000,
  })

  if (isLoading) {
    return <p className="text-sm text-zinc-500 animate-pulse">Loading operational metrics…</p>
  }
  if (isError || !data) {
    return <p className="text-sm text-rose-300">Monitoring unavailable (admin auth required).</p>
  }

  const checks = data.health.checks ?? {}

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Activity className="w-5 h-5 text-cyan-400" />
        <h2 className="font-semibold text-lg">Operations</h2>
        <span
          className={cn(
            'text-xs px-2 py-0.5 rounded-full uppercase tracking-wide',
            data.status === 'healthy'
              ? 'bg-emerald-500/20 text-emerald-300'
              : 'bg-amber-500/20 text-amber-200',
          )}
        >
          {data.status}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          ['Database', checks.database],
          ['Redis', checks.redis],
          ['Celery', checks.celery],
          ['OCR', checks.ocr],
          ['Storage', checks.storage],
        ].map(([label, ok]) => (
          <GlassCard key={label} className="p-3 flex items-center gap-2">
            <StatusDot ok={Boolean(ok)} />
            <span className="text-xs text-zinc-400">{label}</span>
          </GlassCard>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Server className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-medium">Celery workers</h3>
          </div>
          <ul className="text-xs text-zinc-400 space-y-1">
            <li>Online: {data.workers.workers_online ?? 0}</li>
            <li>Active tasks: {data.workers.active_tasks ?? 0}</li>
            <li>Reserved: {data.workers.reserved_tasks ?? 0}</li>
            {data.workers.queues && Object.keys(data.workers.queues).length > 0 && (
              <li className="pt-1">
                Queues:{' '}
                {Object.entries(data.workers.queues)
                  .map(([q, n]) => `${q}(${n})`)
                  .join(', ')}
              </li>
            )}
          </ul>
        </GlassCard>

        <GlassCard className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-medium">Exports</h3>
          </div>
          <ul className="text-xs text-zinc-400 space-y-1">
            <li>Queue depth: {data.exports.queue_depth ?? 0}</li>
            <li>Queued: {data.exports.queued ?? 0}</li>
            <li className="text-rose-300/90">Failed: {data.exports.failed ?? 0}</li>
          </ul>
        </GlassCard>

        <GlassCard className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-medium">Redis cache</h3>
          </div>
          <p className="text-xs text-zinc-500 mb-2">
            {data.cache.redis?.connected ? 'Connected' : 'Disconnected'} ·{' '}
            {data.cache.enabled ? 'cache on' : 'cache off'}
            {data.cache.redis?.used_memory_human && ` · ${data.cache.redis.used_memory_human}`}
          </p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(data.cache.cache?.hit_rates ?? {}).map(([ns, rate]) => (
              <div key={ns} className="rounded bg-zinc-900/80 px-2 py-1 border border-white/5">
                <span className="text-[10px] text-zinc-500">{ns}</span>
                <p className="text-cyan-300 font-mono text-xs">{(rate * 100).toFixed(0)}%</p>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-zinc-600 mt-2">
            Aggregate hit ratio: {((data.cache.aggregate_hit_ratio ?? 0) * 100).toFixed(0)}%
            {data.cache.redis?.evicted_keys != null &&
              ` · evictions: ${data.cache.redis.evicted_keys}`}
          </p>
        </GlassCard>

        <GlassCard className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <HardDrive className="w-4 h-4 text-zinc-400" />
            <h3 className="text-sm font-medium">OCR engine</h3>
          </div>
          <p className="text-xs text-zinc-400">
            Tesseract: {data.health.ocr?.available ? 'available' : 'unavailable'}
          </p>
          <p className="text-[10px] text-zinc-600 mt-2">
            Prometheus: <code className="text-zinc-500">/api/v1/metrics</code>
          </p>
        </GlassCard>
      </div>
    </div>
  )
}
