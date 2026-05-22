import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle2,
  Download,
  FileOutput,
  Loader2,
  AlertTriangle,
  Bug,
} from 'lucide-react'
import { useState } from 'react'
import { GlassCard } from '@/components/ui/GlassCard'
import { PdfDiffViewer } from '@/components/export/PdfDiffViewer'
import { exportApi } from '@/services/exportApi'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import type { ApplyEditsResponse } from '@/types/export'
import { cn } from '@/utils/cn'

interface ExportWorkflowProps {
  statementId: string
}

export function ExportWorkflow({ statementId }: ExportWorkflowProps) {
  const sessionId = useEditSessionStore((s) => s.sessionId)
  const [result, setResult] = useState<ApplyEditsResponse | null>(null)
  const [showDebug, setShowDebug] = useState(false)

  const exportMutation = useMutation({
    mutationFn: () =>
      exportApi
        .applyEdits({
          statement_id: statementId,
          session_id: sessionId ?? undefined,
        })
        .then((r) => r.data),
    onSuccess: (data) => setResult(data),
  })

  const editedUrl = result
    ? exportApi.previewEdited(statementId)
    : null

  return (
    <div className="space-y-6">
      <GlassCard className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="font-semibold flex items-center gap-2">
            <FileOutput className="w-5 h-5 text-indigo-400" />
            Invisible PDF export
          </h2>
          <p className="text-sm text-zinc-500 mt-1">
            Typography-preserving overlay · original PDF unchanged on disk until export
          </p>
        </div>
        <button
          type="button"
          onClick={() => exportMutation.mutate()}
          disabled={exportMutation.isPending}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 disabled:opacity-50 font-medium text-sm"
        >
          {exportMutation.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <FileOutput className="w-4 h-4" />
          )}
          Apply edits & export
        </button>
      </GlassCard>

      {exportMutation.isError && (
        <p className="text-sm text-red-400">
          Export failed. Ensure edits are committed or session is active.
        </p>
      )}

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="grid sm:grid-cols-3 gap-3">
              <GlassCard className="text-center py-4">
                <p className="text-2xl font-bold text-cyan-400">{result.replacements_applied}</p>
                <p className="text-xs text-zinc-500 mt-1">Regions replaced</p>
              </GlassCard>
              <GlassCard className="text-center py-4">
                <p
                  className={cn(
                    'text-2xl font-bold',
                    result.validation.passed ? 'text-emerald-400' : 'text-amber-400',
                  )}
                >
                  {(result.validation.text_match_ratio * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-zinc-500 mt-1">Text match score</p>
              </GlassCard>
              <GlassCard className="text-center py-4 flex flex-col items-center justify-center">
                {result.validation.passed ? (
                  <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-8 h-8 text-amber-400" />
                )}
                <p className="text-xs text-zinc-500 mt-2">Visual validation</p>
              </GlassCard>
            </div>

            {result.warnings.map((w) => (
              <p key={w} className="text-xs text-amber-500/90">
                {w}
              </p>
            ))}

            <div className="flex flex-wrap gap-3">
              <a
                href={editedUrl ?? '#'}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-white/10 text-sm hover:bg-white/5"
              >
                <Download className="w-4 h-4" />
                Download edited PDF
              </a>
              <label className="inline-flex items-center gap-2 text-sm text-zinc-500 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showDebug}
                  onChange={(e) => setShowDebug(e.target.checked)}
                />
                <Bug className="w-4 h-4" />
                Validation details
              </label>
            </div>

            {showDebug && result.validation.issues.length > 0 && (
              <GlassCard className="text-xs font-mono text-zinc-500 space-y-1">
                {result.validation.issues.map((issue, i) => (
                  <p key={i}>{issue}</p>
                ))}
              </GlassCard>
            )}

            <PdfDiffViewer
              originalUrl={exportApi.previewOriginal(statementId)}
              editedUrl={exportApi.previewEdited(statementId)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
