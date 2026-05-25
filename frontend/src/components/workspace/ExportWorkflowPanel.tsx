import { Download, FileCheck, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { exportQueueApi } from '@/services/exportQueueApi'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import { toast } from '@/components/ui/Toast'
import { cn } from '@/utils/cn'

interface ExportWorkflowPanelProps {
  statementId: string
  validationPassed: boolean
}

export function ExportWorkflowPanel({
  statementId,
  validationPassed,
}: ExportWorkflowPanelProps) {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sessionId = useEditSessionStore((s) => s.sessionId)

  const runExport = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data: job } = await exportQueueApi.queue(statementId, sessionId)
      if (job.status === 'completed' && job.download_url) {
        setDone(true)
        toast('Export ready', 'success')
      } else {
        toast('Export queued — check status shortly', 'info')
        const poll = setInterval(async () => {
          try {
            const { data: j } = await exportQueueApi.getJob(job.id)
            if (j.status === 'completed') {
              clearInterval(poll)
              setDone(true)
              toast('Export completed', 'success')
              setLoading(false)
            } else if (j.status === 'failed') {
              clearInterval(poll)
              setError(j.error_message ?? 'Export failed')
              setLoading(false)
            }
          } catch {
            clearInterval(poll)
          }
        }, 2000)
        setTimeout(() => clearInterval(poll), 120000)
        return
      }
    } catch {
      setError('Export failed — commit edits and validate first.')
      toast('Export failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 space-y-3 border-t border-white/10">
      <p className="text-xs text-zinc-500 uppercase tracking-wider">Export</p>
      <button
        type="button"
        onClick={runExport}
        disabled={loading || !validationPassed}
        className={cn(
          'w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm',
          validationPassed
            ? 'bg-indigo-600 hover:bg-indigo-500'
            : 'bg-zinc-800 text-zinc-500 cursor-not-allowed',
        )}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileCheck className="w-4 h-4" />
        )}
        Apply & export PDF
      </button>
      {done && (
        <a
          href={`${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}/preview/${statementId}/edited`}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-2 text-xs text-cyan-400 hover:text-cyan-300"
        >
          <Download className="w-4 h-4" />
          Download edited PDF
        </a>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}
