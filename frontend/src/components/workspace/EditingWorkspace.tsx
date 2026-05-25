import { Loader2, Save } from 'lucide-react'
import { useEffect } from 'react'
import { PDFCanvas } from '@/components/pdf-editor/PDFCanvas'
import { EditToolbar } from '@/components/pdf-editor/EditToolbar'
import { WorkspaceLeftSidebar } from '@/components/workspace/WorkspaceLeftSidebar'
import { WorkspaceRightSidebar } from '@/components/workspace/WorkspaceRightSidebar'
import { useEditSession } from '@/hooks/useEditSession'
import { useEditWebSocket } from '@/hooks/useEditWebSocket'
import { useLiveEditSync } from '@/hooks/useLiveEditSync'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { statementsApi } from '@/services/api'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import { usePdfStore } from '@/store/usePdfStore'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import type { ChangeType } from '@/types/editSession'

interface EditingWorkspaceProps {
  statementId: string
}

export function EditingWorkspace({ statementId }: EditingWorkspaceProps) {
  const {
    sessionId,
    state,
    loading,
    error,
    updateTransaction,
    isUpdating,
    undo,
    redo,
    commit,
    canUndo,
    canRedo,
    isCommitting,
  } = useEditSession(statementId)

  const setPdfEditTarget = useWorkspaceStore((s) => s.setPdfEditTarget)
  const setPdfScale = useWorkspaceStore((s) => s.setPdfScale)
  const pdfScale = useWorkspaceStore((s) => s.pdfScale)
  const setStatement = usePdfStore((s) => s.setStatement)
  const fileUrl = usePdfStore((s) => s.fileUrl) ?? statementsApi.previewUrl(statementId)

  useEditWebSocket(sessionId)

  const { updateWithSync } = useLiveEditSync({
    updateTransaction: (args) => updateTransaction(args),
    state,
  })

  useEffect(() => {
    setStatement(statementId, '', fileUrl)
    return () => {
      useWorkspaceStore.getState().reset()
    }
  }, [statementId, fileUrl, setStatement])

  useEffect(() => {
    if (state?.propagation_trace?.length) {
      useWorkspaceStore
        .getState()
        .flashTransactions([...new Set(state.propagation_trace.map((t) => t.transaction_id))])
    }
  }, [state?.propagation_trace])

  useKeyboardShortcuts(
    {
      onUndo: () => undo(),
      onRedo: () => redo(),
      onEscape: () => setPdfEditTarget(null),
      onZoomIn: () => setPdfScale(pdfScale + 0.1),
      onZoomOut: () => setPdfScale(pdfScale - 0.1),
      onFit: () => setPdfScale(1),
    },
    Boolean(state),
  )

  const handleFieldCommit = (transactionId: string, field: ChangeType, value: string | null) => {
    updateWithSync(transactionId, field, value)
  }

  if (loading && !state) {
    return (
      <div className="flex items-center justify-center h-[70vh] text-zinc-500">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mr-3" />
        Initializing workspace…
      </div>
    )
  }

  if (error) return <p className="text-red-400 p-6">{error}</p>
  if (!state) return null

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] w-full">
      <div className="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-zinc-950/90">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Editing Workspace</h1>
          <p className="text-xs text-zinc-500">
            {state.bank.replace(/_/g, ' ')} · Real-time sync
          </p>
        </div>
        <button
          type="button"
          onClick={() => commit('Workspace commit')}
          disabled={isCommitting || state.modified_count === 0}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40"
        >
          {isCommitting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          Commit
        </button>
      </div>

      <EditToolbar
        statementId={statementId}
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={undo}
        onRedo={redo}
        isUpdating={isUpdating}
      />

      <div className="flex flex-1 min-h-0">
        <WorkspaceLeftSidebar
          statementId={statementId}
          state={state}
          onUpdate={handleFieldCommit}
          isUpdating={isUpdating}
        />
        <main className="flex-1 min-w-0 p-3 overflow-hidden">
          <PDFCanvas
            fileUrl={fileUrl}
            state={state}
            onFieldCommit={handleFieldCommit}
          />
        </main>
        <WorkspaceRightSidebar state={state} isUpdating={isUpdating} />
      </div>
    </div>
  )
}
