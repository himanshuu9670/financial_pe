import { RefreshCw, Sparkles } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { ConfidenceMeter } from '@/components/ai/ConfidenceMeter'
import { CategoryBreakdownChart } from '@/components/ai/CategoryBreakdownChart'
import { AnomalyAlerts } from '@/components/ai/AnomalyAlerts'
import { SmartSuggestionsPanel } from '@/components/ai/SmartSuggestionsPanel'
import { SemanticSearchBar } from '@/components/ai/SemanticSearchBar'
import { AiDebugPanel } from '@/components/ai/AiDebugPanel'
import {
  useAiInsights,
  useAiCategories,
  useAiAnomalies,
  useAiSuggestions,
  useAiStatus,
} from '@/hooks/useAiIntelligence'
import { SpendingTrendChart } from '@/components/ai/SpendingTrendChart'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import { aiApi } from '@/services/aiApi'
import { Link } from 'react-router-dom'

interface AiInsightsPanelProps {
  statementId: string
}

export function AiInsightsPanel({ statementId }: AiInsightsPanelProps) {
  const showDebug = useWorkspaceStore((s) => s.showDebugTools)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)
  const qc = useQueryClient()

  const aiStatus = useAiStatus(statementId, true)
  const insights = useAiInsights(statementId)
  const categories = useAiCategories(statementId)
  const anomalies = useAiAnomalies(statementId)
  const suggestions = useAiSuggestions(statementId)

  const loading =
    insights.isLoading ||
    categories.isLoading ||
    anomalies.isLoading ||
    aiStatus.data?.processing?.status === 'running'

  const invalidateAll = () => {
    qc.invalidateQueries({ queryKey: ['ai-insights', statementId] })
    qc.invalidateQueries({ queryKey: ['ai-categories', statementId] })
    qc.invalidateQueries({ queryKey: ['ai-anomalies', statementId] })
    qc.invalidateQueries({ queryKey: ['ai-suggestions', statementId] })
    qc.invalidateQueries({ queryKey: ['ai-status', statementId] })
  }

  const refresh = async (asyncMode = false) => {
    await aiApi.triggerAnalyze(statementId, asyncMode)
    invalidateAll()
  }

  if (loading) {
    return (
      <div className="p-4 text-sm text-zinc-500 animate-pulse">
        Running financial intelligence…
      </div>
    )
  }

  if (insights.isError) {
    const statusCode = (insights.error as { response?: { status?: number } })?.response?.status
    const msg =
      statusCode === 409
        ? 'Parse transactions first (Transactions page or workspace), then run AI.'
        : 'AI analysis unavailable. Check backend logs and retry.'
    return (
      <div className="p-4 text-sm text-rose-300 space-y-2">
        <p>{msg}</p>
        <button
          type="button"
          onClick={() => void refresh(false)}
          className="text-cyan-400 text-xs hover:text-cyan-300"
        >
          Run AI analysis (sync)
        </button>
        <button
          type="button"
          onClick={() => void refresh(true)}
          className="block text-indigo-400 text-xs hover:text-indigo-300"
        >
          Queue background AI job
        </button>
      </div>
    )
  }

  const ins = insights.data!
  const anom = anomalies.data
  const sug = suggestions.data

  return (
    <div className="flex flex-col h-full overflow-y-auto px-3 py-2 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-zinc-200 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          AI Financial Intelligence
        </h3>
        {ins.cached && (
          <span className="text-[9px] text-zinc-600 uppercase tracking-wide">cached</span>
        )}
        <button
          type="button"
          onClick={() => void refresh(false)}
          className="p-1 text-zinc-500 hover:text-cyan-300"
          title="Refresh AI"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      <ConfidenceMeter confidence={ins.confidence} compact />

      <SemanticSearchBar
        statementId={statementId}
        onSelect={(id) => selectTransaction(id)}
      />

      <SpendingTrendChart data={ins.category_spend} />
      <CategoryBreakdownChart data={ins.category_spend} />

      {anom && (
        <AnomalyAlerts
          anomalies={anom.anomalies}
          fraud={anom.fraud}
          onSelect={(id) => selectTransaction(id)}
        />
      )}

      {sug && (
        <SmartSuggestionsPanel
          suggestions={sug.suggestions}
          corrections={sug.corrections}
        />
      )}

      <Link
        to={`/insights/${statementId}`}
        className="text-[11px] text-center text-indigo-400 hover:text-indigo-300 py-2"
      >
        Open full insights dashboard →
      </Link>

      {showDebug && categories.data && anom && (
        <AiDebugPanel
          confidence={ins.confidence}
          categories={categories.data.categories}
          anomalies={anom.anomalies}
          cached={ins.cached}
        />
      )}
    </div>
  )
}
