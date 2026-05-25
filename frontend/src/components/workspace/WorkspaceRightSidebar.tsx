import { Activity, FileText, Shield, Sparkles, Type } from 'lucide-react'
import { useAiInsights } from '@/hooks/useAiIntelligence'
import { ConfidenceMeter } from '@/components/ai/ConfidenceMeter'
import { LiveSummaryDashboard } from '@/components/workspace/LiveSummaryDashboard'
import { LiveValidationPanel } from '@/components/workspace/LiveValidationPanel'
import { TransactionDetailsPanel } from '@/components/workspace/TransactionDetailsPanel'
import { TypographyInspector } from '@/components/workspace/TypographyInspector'
import { DebugToolsPanel } from '@/components/workspace/DebugToolsPanel'
import { ExportWorkflowPanel } from '@/components/workspace/ExportWorkflowPanel'
import type { SessionStateResponse } from '@/types/editSession'
import { useWorkspaceStore, type RightPanelTab } from '@/store/useWorkspaceStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import { cn } from '@/utils/cn'

const tabs: { id: RightPanelTab; label: string; icon: typeof FileText }[] = [
  { id: 'summary', label: 'Summary', icon: Activity },
  { id: 'ai', label: 'AI', icon: Sparkles },
  { id: 'details', label: 'Details', icon: FileText },
  { id: 'validation', label: 'Validation', icon: Shield },
  { id: 'typography', label: 'Typography', icon: Type },
]

interface WorkspaceRightSidebarProps {
  state: SessionStateResponse
  isUpdating: boolean
}

export function WorkspaceRightSidebar({ state, isUpdating }: WorkspaceRightSidebarProps) {
  const tab = useWorkspaceStore((s) => s.rightTab)
  const setTab = useWorkspaceStore((s) => s.setRightTab)
  const showDebug = useWorkspaceStore((s) => s.showDebugTools)
  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const entry = state.entries.find((e) => e.transaction_id === selectedId)
  const aiInsights = useAiInsights(state.statement_id)

  return (
    <aside className="w-[300px] shrink-0 flex flex-col border-l border-white/10 bg-zinc-950/60 backdrop-blur-xl h-full">
      <nav className="flex border-b border-white/10">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={cn(
              'flex-1 py-2 flex justify-center',
              tab === id ? 'text-cyan-300 bg-cyan-500/10' : 'text-zinc-500',
            )}
            title={label}
          >
            <Icon className="w-4 h-4" />
          </button>
        ))}
      </nav>
      <div className="flex-1 overflow-y-auto">
        {tab === 'summary' && <LiveSummaryDashboard state={state} />}
        {tab === 'ai' && aiInsights.data && (
          <div className="p-3">
            <ConfidenceMeter confidence={aiInsights.data.confidence} compact />
          </div>
        )}
        {tab === 'ai' && aiInsights.isLoading && (
          <p className="p-4 text-xs text-zinc-500">Loading AI metrics…</p>
        )}
        {tab === 'details' && <TransactionDetailsPanel entry={entry} />}
        {tab === 'validation' && (
          <LiveValidationPanel state={state} isUpdating={isUpdating} />
        )}
        {tab === 'typography' && <TypographyInspector entry={entry} />}
      </div>
      <ExportWorkflowPanel
        statementId={state.statement_id}
        validationPassed={state.validation_passed}
      />
      {showDebug && <DebugToolsPanel state={state} />}
    </aside>
  )
}
