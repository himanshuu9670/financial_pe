import { motion } from 'framer-motion'
import {
  Bug,
  Loader2,
  Redo2,
  Save,
  Undo2,
} from 'lucide-react'
import { useEffect } from 'react'
import { GlassCard } from '@/components/ui/GlassCard'
import { DependencyGraphPanel } from '@/components/edit/DependencyGraphPanel'
import { EditableTransactionTable } from '@/components/edit/EditableTransactionTable'
import { FinancialSummaryCards } from '@/components/edit/FinancialSummaryCards'
import { Link } from 'react-router-dom'
import { useEditSession } from '@/hooks/useEditSession'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import { useTransactionStore } from '@/store/useTransactionStore'

interface EditModeExplorerProps {
  statementId: string
}

export function EditModeExplorer({ statementId }: EditModeExplorerProps) {
  const {
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

  const debugMode = useEditSessionStore((s) => s.debugMode)
  const setDebugMode = useEditSessionStore((s) => s.setDebugMode)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)

  useEffect(() => {
    return () => useEditSessionStore.getState().clear()
  }, [])

  if (loading && !state) {
    return (
      <div className="flex items-center justify-center py-24 text-zinc-500">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mr-3" />
        Starting edit session…
      </div>
    )
  }

  if (error) {
    return <p className="text-red-400 text-sm">{error}</p>
  }

  if (!state) return null

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => undo()}
          disabled={!canUndo || isUpdating}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border border-white/10 disabled:opacity-40 hover:bg-white/5"
        >
          <Undo2 className="w-4 h-4" />
          Undo
        </button>
        <button
          type="button"
          onClick={() => redo()}
          disabled={!canRedo || isUpdating}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border border-white/10 disabled:opacity-40 hover:bg-white/5"
        >
          <Redo2 className="w-4 h-4" />
          Redo
        </button>
        <button
          type="button"
          onClick={() => commit('Phase 4 session commit')}
          disabled={isCommitting}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50"
        >
          {isCommitting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          Commit edits
        </button>

        <label className="inline-flex items-center gap-2 text-sm text-zinc-500 cursor-pointer ml-auto">
          <input
            type="checkbox"
            checked={debugMode}
            onChange={(e) => setDebugMode(e.target.checked)}
          />
          <Bug className="w-4 h-4" />
          Debug
        </label>

        {state.modified_count > 0 && (
          <span className="text-xs text-amber-400">
            {state.modified_count} row(s) changed
          </span>
        )}
        {isUpdating && (
          <span className="text-xs text-cyan-400 flex items-center gap-1">
            <Loader2 className="w-3 h-3 animate-spin" />
            Recalculating…
          </span>
        )}
      </div>

      <FinancialSummaryCards
        summary={state.summary}
        validationPassed={state.validation_passed}
      />

      {!state.validation_passed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-amber-400 glass rounded-lg px-4 py-2 border border-amber-500/20"
        >
          {state.validation_issues.join(' · ')}
        </motion.div>
      )}

      {state.propagation_trace.length > 0 && (
        <GlassCard className="text-xs text-indigo-300/80">
          <p className="text-zinc-500 mb-2">Last propagation ({state.propagation_trace.length} updates)</p>
          <ul className="space-y-1 max-h-24 overflow-y-auto font-mono">
            {state.propagation_trace.slice(0, 8).map((t, i) => (
              <li key={i}>
                {t.transaction_id.slice(0, 8)}… {t.field}: {t.old_value} → {t.new_value}
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      <GlassCard className="p-0 flex flex-col min-h-[520px] overflow-hidden">
          <div className="p-3 border-b border-white/10">
            <h2 className="font-semibold text-sm">Editable ledger</h2>
            <p className="text-xs text-zinc-500 mt-0.5">
              Click amounts to edit · amber = modified · indigo = propagated
            </p>
          </div>
          <EditableTransactionTable
            state={state}
            onUpdate={(id, field, value) => {
              updateTransaction({ transactionId: id, field, value })
              selectTransaction(id)
            }}
            isUpdating={isUpdating}
          />
      </GlassCard>

      {debugMode && (
        <DependencyGraphPanel
          nodes={state.dependency_graph}
          entries={state.entries}
          selectedId={useTransactionStore.getState().selectedTransactionId}
        />
      )}

      <p className="text-sm text-zinc-500">
        <Link
          to={`/transactions/${statementId}`}
          className="text-indigo-400 hover:text-indigo-300"
        >
          Open PDF ↔ table sync view
        </Link>
        {' '}to highlight rows on the statement. PDF text replacement ships in Phase 5.
      </p>
    </div>
  )
}
