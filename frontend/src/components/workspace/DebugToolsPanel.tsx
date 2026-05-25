import type { SessionStateResponse } from '@/types/editSession'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'

interface DebugToolsPanelProps {
  state: SessionStateResponse
}

export function DebugToolsPanel({ state }: DebugToolsPanelProps) {
  const pdfEditTarget = useWorkspaceStore((s) => s.pdfEditTarget)

  return (
    <div className="p-4 space-y-2 text-[10px] font-mono text-zinc-500 max-h-64 overflow-auto">
      <p className="text-pink-400">Coordinate inspector</p>
      <p>Session: {state.session_id.slice(0, 8)}…</p>
      <p>Entries: {state.entries.length}</p>
      <p>Graph nodes: {state.dependency_graph.length}</p>
      {pdfEditTarget && (
        <pre className="bg-black/40 p-2 rounded text-cyan-300/80">
          {JSON.stringify(pdfEditTarget, null, 2)}
        </pre>
      )}
    </div>
  )
}
