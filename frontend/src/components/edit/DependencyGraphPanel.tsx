import type { DependencyNode, LedgerEntry } from '@/types/editSession'
import { GlassCard } from '@/components/ui/GlassCard'
import { cn } from '@/utils/cn'

export function DependencyGraphPanel({
  nodes,
  entries,
  selectedId,
}: {
  nodes: DependencyNode[]
  entries: LedgerEntry[]
  selectedId: string | null
}) {
  const byId = Object.fromEntries(entries.map((e) => [e.transaction_id, e]))

  return (
    <GlassCard className="text-xs font-mono space-y-2 max-h-48 overflow-y-auto">
      <p className="text-zinc-500 uppercase tracking-wider text-[10px]">Dependency chain</p>
      {nodes.slice(0, 24).map((node) => {
        const entry = byId[node.transaction_id]
        const isSel = selectedId === node.transaction_id
        return (
          <div
            key={node.transaction_id}
            className={cn(
              'flex items-center gap-2 py-1 px-2 rounded border border-transparent',
              isSel && 'border-cyan-500/40 bg-cyan-500/10',
            )}
          >
            <span className="text-zinc-600 w-4">{node.index}</span>
            <span className="text-zinc-400 truncate flex-1">
              {entry?.description?.slice(0, 28) ?? node.transaction_id.slice(0, 8)}
            </span>
            <span className="text-cyan-500/80">{entry?.balance != null ? Number(entry.balance).toFixed(0) : '—'}</span>
          </div>
        )
      })}
      {nodes.length > 24 && (
        <p className="text-zinc-600">+{nodes.length - 24} more nodes</p>
      )}
    </GlassCard>
  )
}
