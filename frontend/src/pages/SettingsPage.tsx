import { GlassCard } from '@/components/ui/GlassCard'

export function SettingsPage() {
  const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-zinc-500 mt-1">Environment and application configuration</p>
      </div>

      <GlassCard>
        <h2 className="font-semibold mb-4">API Configuration</h2>
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between gap-4 py-2 border-b border-white/5">
            <dt className="text-zinc-500">API Base URL</dt>
            <dd className="font-mono text-indigo-300">{apiBase}</dd>
          </div>
          <div className="flex justify-between gap-4 py-2 border-b border-white/5">
            <dt className="text-zinc-500">Mode</dt>
            <dd>{import.meta.env.MODE}</dd>
          </div>
          <div className="flex justify-between gap-4 py-2">
            <dt className="text-zinc-500">Build</dt>
            <dd>Production-ready release</dd>
          </div>
        </dl>
      </GlassCard>

      <GlassCard>
        <h2 className="font-semibold mb-2">Supported banks (planned)</h2>
        <p className="text-sm text-zinc-500">YES Bank · Axis Bank · Canara Bank · extensible registry</p>
      </GlassCard>
    </div>
  )
}
