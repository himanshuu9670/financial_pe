import { Brain, FileText, History, Table2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { VirtualizedLedgerTable } from '@/components/workspace/VirtualizedLedgerTable'
import { AiInsightsPanel } from '@/components/ai/AiInsightsPanel'
import { EditHistoryTimeline } from '@/components/workspace/EditHistoryTimeline'
import type { SessionStateResponse } from '@/types/editSession'
import type { ChangeType } from '@/types/editSession'
import { useWorkspaceStore, type LeftPanelTab } from '@/store/useWorkspaceStore'
import { cn } from '@/utils/cn'

const tabs: { id: LeftPanelTab; label: string; icon: typeof Table2 }[] = [
  { id: 'transactions', label: 'Transactions', icon: Table2 },
  { id: 'history', label: 'History', icon: History },
  { id: 'insights', label: 'AI Insights', icon: Brain },
  { id: 'statements', label: 'Statements', icon: FileText },
]

interface WorkspaceLeftSidebarProps {
  statementId: string
  state: SessionStateResponse
  onUpdate: (id: string, field: ChangeType, value: string | null) => void
  isUpdating: boolean
}

export function WorkspaceLeftSidebar({
  statementId,
  state,
  onUpdate,
  isUpdating,
}: WorkspaceLeftSidebarProps) {
  const tab = useWorkspaceStore((s) => s.leftTab)
  const setTab = useWorkspaceStore((s) => s.setLeftTab)

  return (
    <aside className="w-[320px] shrink-0 flex flex-col border-r border-white/10 bg-zinc-950/60 backdrop-blur-xl h-full">
      <nav className="flex border-b border-white/10">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={cn(
              'flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] transition-colors',
              tab === id ? 'text-cyan-300 bg-cyan-500/10' : 'text-zinc-500 hover:text-zinc-300',
            )}
            title={label}
          >
            <Icon className="w-4 h-4" />
            <span className="truncate px-0.5">{label.split(' ')[0]}</span>
          </button>
        ))}
      </nav>

      <div className="flex-1 min-h-0 overflow-hidden py-2">
        {tab === 'transactions' && (
          <VirtualizedLedgerTable state={state} onUpdate={onUpdate} isUpdating={isUpdating} />
        )}
        {tab === 'history' && <EditHistoryTimeline state={state} />}
        {tab === 'insights' && <AiInsightsPanel statementId={statementId} />}
        {tab === 'statements' && (
          <div className="p-4 text-sm">
            <Link to="/statements" className="text-indigo-400 hover:text-indigo-300">
              All statements →
            </Link>
          </div>
        )}
      </div>
    </aside>
  )
}
