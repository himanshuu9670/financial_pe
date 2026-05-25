import { useNavigate, useParams } from 'react-router-dom'
import { EditHistoryTimeline } from '@/components/workspace/EditHistoryTimeline'
import { useEditSession } from '@/hooks/useEditSession'
import { UploadZone } from '@/components/pdf/UploadZone'
import { useAppStore } from '@/store/useAppStore'
import { Loader2 } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'

export function HistoryPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId
  const { state, loading, error } = useEditSession(statementId ?? undefined)

  if (!statementId) {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <UploadZone onUploaded={(sid) => navigate(`/history/${sid}`)} />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold mb-4">Edit history</h1>
      {loading && !state && (
        <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
      )}
      {error && <p className="text-red-400">{error}</p>}
      {state && (
        <GlassCard>
          <EditHistoryTimeline state={state} />
        </GlassCard>
      )}
    </div>
  )
}
