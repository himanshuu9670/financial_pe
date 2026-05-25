import type { ConfidenceBreakdown } from '@/types/ai'
import type { CategoryItem, AnomalyItem } from '@/types/ai'

interface AiDebugPanelProps {
  confidence: ConfidenceBreakdown
  categories: CategoryItem[]
  anomalies: AnomalyItem[]
  cached?: boolean
}

export function AiDebugPanel({ confidence, categories, anomalies, cached }: AiDebugPanelProps) {
  return (
    <div className="font-mono text-[10px] text-zinc-400 space-y-2 p-2 rounded-lg bg-black/40 border border-white/5">
      <p className="text-zinc-500">AI debug · cached={String(cached)}</p>
      <pre className="overflow-x-auto">{JSON.stringify(confidence, null, 2)}</pre>
      <p>Categories sample: {categories.slice(0, 3).map((c) => c.category).join(', ')}</p>
      <p>Anomalies: {anomalies.length} total</p>
    </div>
  )
}
