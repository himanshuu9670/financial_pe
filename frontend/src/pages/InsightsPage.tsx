import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { GlassCard } from '@/components/ui/GlassCard'
import { StatCard } from '@/components/ui/StatCard'
import { ConfidenceMeter } from '@/components/ai/ConfidenceMeter'
import { CategoryBreakdownChart } from '@/components/ai/CategoryBreakdownChart'
import { SpendingTrendChart } from '@/components/ai/SpendingTrendChart'
import { AnomalyAlerts } from '@/components/ai/AnomalyAlerts'
import { SmartSuggestionsPanel } from '@/components/ai/SmartSuggestionsPanel'
import { SemanticSearchBar } from '@/components/ai/SemanticSearchBar'
import {
  useAiInsights,
  useAiAnomalies,
  useAiSuggestions,
  useAiCategories,
} from '@/hooks/useAiIntelligence'
import { Sparkles, TrendingUp, AlertCircle } from 'lucide-react'

export function InsightsPage() {
  const { id } = useParams()
  const statementId = id ?? ''

  const insights = useAiInsights(statementId)
  const anomalies = useAiAnomalies(statementId)
  const suggestions = useAiSuggestions(statementId)
  const categories = useAiCategories(statementId)

  if (!statementId) {
    return (
      <div className="p-8 text-zinc-400">
        Select a statement from{' '}
        <a href="/statements" className="text-indigo-400">
          Statements
        </a>
      </div>
    )
  }

  if (insights.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-zinc-500">
        <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.5 }}>
          Analyzing financial patterns…
        </motion.div>
      </div>
    )
  }

  if (!insights.data) {
    return <div className="p-8 text-rose-300">Failed to load AI insights.</div>
  }

  const ins = insights.data
  const barData = ins.category_spend.map((c) => ({
    name: c.category,
    debit: c.total_debit,
    count: c.count,
  }))

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <header className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30">
          <Sparkles className="w-6 h-6 text-indigo-300" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">AI Insights Dashboard</h1>
          <p className="text-sm text-zinc-500">Statement {statementId.slice(0, 8)}…</p>
        </div>
      </header>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="AI Confidence"
          value={`${Math.round(ins.confidence.overall * 100)}%`}
          icon={TrendingUp}
        />
        <StatCard
          label="Risk Score"
          value={`${Math.round(ins.fraud.risk_score * 100)}%`}
          icon={AlertCircle}
        />
        <StatCard label="Anomalies" value={String(ins.anomaly_count)} icon={AlertCircle} />
        <StatCard label="Top Category" value={ins.top_category ?? '—'} icon={Sparkles} />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="text-sm font-medium text-zinc-300 mb-3">Extraction confidence</h2>
          <ConfidenceMeter confidence={ins.confidence} />
        </GlassCard>
        <GlassCard>
          <h2 className="text-sm font-medium text-zinc-300 mb-3">Spending trend</h2>
          <SpendingTrendChart data={ins.category_spend} />
        </GlassCard>
      </div>

      <GlassCard>
        <h2 className="text-sm font-medium text-zinc-300 mb-3">Category breakdown</h2>
        <CategoryBreakdownChart data={ins.category_spend} />
      </GlassCard>

      <GlassCard>
        <h2 className="text-sm font-medium text-zinc-300 mb-3">Category spend (debit)</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#a1a1aa' }} />
              <YAxis tick={{ fontSize: 10, fill: '#a1a1aa' }} />
              <Tooltip
                contentStyle={{
                  background: '#18181b',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 8,
                }}
              />
              <Bar dataKey="debit" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      <div className="grid md:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="text-sm font-medium text-zinc-300 mb-3">Anomalies & fraud</h2>
          {anomalies.data && (
            <AnomalyAlerts anomalies={anomalies.data.anomalies} fraud={anomalies.data.fraud} />
          )}
        </GlassCard>
        <GlassCard>
          <h2 className="text-sm font-medium text-zinc-300 mb-3">Smart suggestions</h2>
          {suggestions.data && (
            <SmartSuggestionsPanel
              suggestions={suggestions.data.suggestions}
              corrections={suggestions.data.corrections}
            />
          )}
        </GlassCard>
      </div>

      <GlassCard>
        <h2 className="text-sm font-medium text-zinc-300 mb-3">Semantic search</h2>
        <SemanticSearchBar statementId={statementId} />
      </GlassCard>

      {categories.data && (
        <GlassCard>
          <h2 className="text-sm font-medium text-zinc-300 mb-3">Transaction categories (sample)</h2>
          <ul className="text-xs text-zinc-400 max-h-40 overflow-y-auto space-y-1">
            {categories.data.categories.slice(0, 20).map((c) => (
              <li key={c.transaction_id} className="flex justify-between gap-2">
                <span className="truncate text-zinc-300">{c.description}</span>
                <span className="text-indigo-300 shrink-0">
                  {c.category} ({Math.round(c.confidence * 100)}%)
                </span>
              </li>
            ))}
          </ul>
        </GlassCard>
      )}
    </div>
  )
}
