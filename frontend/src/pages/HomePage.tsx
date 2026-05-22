import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowRight, FileText, Shield, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { StatCard } from '@/components/ui/StatCard'
import { GlassCard } from '@/components/ui/GlassCard'
import { healthApi } from '@/services/api'

export function HomePage() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthApi.check().then((r) => r.data),
    retry: false,
  })

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-3"
      >
        <p className="text-xs font-medium text-indigo-400 uppercase tracking-widest">
          Bank Statement PDF Editor
        </p>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          Edit statements with <span className="gradient-text">invisible precision</span>
        </h1>
        <p className="text-zinc-400 max-w-2xl text-lg">
          Typography-preserving edits, automatic balance recalculation, and multi-bank layout
          intelligence — built for enterprise fintech workflows.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          label="API Status"
          value={health?.status === 'ok' ? 'Online' : 'Starting'}
          icon={Zap}
          trend={health ? `DB: ${health.database ? '✓' : '—'} · Redis: ${health.redis ? '✓' : '—'}` : 'Connect backend'}
          accent="cyan"
        />
        <StatCard
          label="Statements"
          value="—"
          icon={FileText}
          trend="Phase 2: auto-detection"
          accent="indigo"
          delay={0.05}
        />
        <StatCard
          label="Banks Supported"
          value="3+"
          icon={Shield}
          trend="YES · AXIS · CANARA"
          accent="purple"
          delay={0.1}
        />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <GlassCard delay={0.15}>
          <h2 className="text-lg font-semibold mb-2">Quick start</h2>
          <p className="text-sm text-zinc-500 mb-6">
            Upload a bank statement PDF. Extraction and editing activate in upcoming phases.
          </p>
          <Link
            to="/statements"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-medium transition-colors"
          >
            Go to Statements
            <ArrowRight className="w-4 h-4" />
          </Link>
        </GlassCard>

        <GlassCard delay={0.2}>
          <h2 className="text-lg font-semibold mb-2">Architecture</h2>
          <ul className="text-sm text-zinc-500 space-y-2">
            <li>· PDF engine — coordinate extraction (Phase 2)</li>
            <li>· Financial engine — balance recalculation (Phase 3)</li>
            <li>· Typography engine — invisible edits (Phase 4)</li>
            <li>· Multi-bank layout profiles (Phase 6)</li>
          </ul>
        </GlassCard>
      </div>
    </div>
  )
}
