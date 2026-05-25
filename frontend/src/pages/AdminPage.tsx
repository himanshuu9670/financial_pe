import { useQuery } from '@tanstack/react-query'
import { Shield } from 'lucide-react'
import { apiClient } from '@/services/api'
import { AdminMonitoringPanel } from '@/components/admin/AdminMonitoringPanel'
import { AdminQaDashboardPanel } from '@/components/admin/AdminQaDashboardPanel'
import { GlassCard } from '@/components/ui/GlassCard'

interface AdminStats {
  users: number
  statements: number
  exports_queued: number
  exports_failed: number
  audit_events_24h: number
}

export function AdminPage() {
  const { data: stats } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => apiClient.get<AdminStats>('/admin/stats').then((r) => r.data),
  })

  const { data: status } = useQuery({
    queryKey: ['system-status'],
    queryFn: () => apiClient.get('/system-status').then((r) => r.data),
    refetchInterval: 15000,
  })

  const { data: cacheStats } = useQuery({
    queryKey: ['admin-cache-stats'],
    queryFn: () =>
      apiClient
        .get<{ redis_connected: boolean; cache_enabled: boolean; stats: Record<string, unknown> }>(
          '/admin/cache-stats',
        )
        .then((r) => r.data),
    refetchInterval: 10000,
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Shield className="w-6 h-6 text-indigo-400" />
        <h1 className="text-2xl font-bold">Admin dashboard</h1>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            ['Users', stats.users],
            ['Statements', stats.statements],
            ['Exports queued', stats.exports_queued],
            ['Exports failed', stats.exports_failed],
            ['Audit (24h)', stats.audit_events_24h],
          ].map(([label, val]) => (
            <GlassCard key={label as string} className="p-4">
              <p className="text-xs text-zinc-500">{label}</p>
              <p className="text-2xl font-bold mt-1">{val}</p>
            </GlassCard>
          ))}
        </div>
      )}

      <AdminMonitoringPanel />
      <AdminQaDashboardPanel />

      {cacheStats && (
        <GlassCard className="p-4">
          <h2 className="font-semibold mb-2">Redis cache</h2>
          <p className="text-xs text-zinc-500 mb-2">
            Redis {cacheStats.redis_connected ? 'connected' : 'down'} · cache{' '}
            {cacheStats.cache_enabled ? 'enabled' : 'disabled'}
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs mb-3">
            {Object.entries(
              (cacheStats.stats.hit_rates as Record<string, number>) || {},
            ).map(([ns, rate]) => (
              <div key={ns} className="rounded-lg bg-zinc-900/80 px-2 py-1.5 border border-white/5">
                <span className="text-zinc-500">{ns}</span>
                <p className="text-cyan-300 font-mono">{(rate * 100).toFixed(0)}% hit</p>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-zinc-600">
            OCR savings (hits): {String(cacheStats.stats.ocr_savings_estimate ?? 0)} · extraction:{' '}
            {String(cacheStats.stats.extraction_savings_estimate ?? 0)}
          </p>
        </GlassCard>
      )}

      {status && (
        <GlassCard className="p-4">
          <div className="flex flex-wrap items-center gap-3 justify-between">
            <div>
              <h2 className="font-semibold">System status</h2>
              <p className="text-sm text-zinc-500 mt-1">Operational summary for core backend services.</p>
            </div>
            {'status' in status && typeof status.status === 'string' && (
              <span
                className={
                  status.status === 'healthy'
                    ? 'text-emerald-300 bg-emerald-500/10 rounded-full px-3 py-1 text-xs uppercase tracking-wide'
                    : 'text-amber-200 bg-amber-500/10 rounded-full px-3 py-1 text-xs uppercase tracking-wide'
                }
              >
                {status.status}
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mt-4">
            {Object.entries(status)
              .flatMap(([key, value]) =>
                value && typeof value === 'object' && !Array.isArray(value)
                  ? Object.entries(value).map(([subKey, subValue]) => [
                      `${key}.${subKey}`,
                      typeof subValue === 'string' || typeof subValue === 'number' || typeof subValue === 'boolean'
                        ? String(subValue)
                        : JSON.stringify(subValue),
                    ] as const)
                  : [[key, String(value)]] as const,
              )
              .slice(0, 8)
              .map(([key, value]) => (
                <div
                  key={key}
                  className="rounded-2xl bg-zinc-950/80 border border-white/10 p-3"
                >
                  <p className="text-[10px] uppercase tracking-wider text-zinc-500">{key}</p>
                  <p className="mt-1 text-sm text-zinc-100 break-words">{value}</p>
                </div>
              ))}
          </div>
        </GlassCard>
      )}
    </div>
  )
}
