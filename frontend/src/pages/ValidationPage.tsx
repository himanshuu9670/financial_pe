import { useNavigate, useParams } from 'react-router-dom'
import { LiveValidationPanel } from '@/components/workspace/LiveValidationPanel'
import { LiveSummaryDashboard } from '@/components/workspace/LiveSummaryDashboard'
import { useEditSession } from '@/hooks/useEditSession'
import { UploadZone } from '@/components/pdf/UploadZone'
import { useAppStore } from '@/store/useAppStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'

export function ValidationPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId
  const { state, loading, error } = useEditSession(statementId ?? undefined)

  if (!statementId) {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <UploadZone onUploaded={(sid) => navigate(`/validation/${sid}`)} />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-xl font-bold">Validation dashboard</h1>
      {loading && !state && <Loader2 className="w-6 h-6 animate-spin" />}
      {error && <p className="text-red-400">{error}</p>}
      {state && (
        <>
          <GlassCard>
            <LiveSummaryDashboard state={state} />
          </GlassCard>
          <GlassCard>
            <LiveValidationPanel state={state} />
          </GlassCard>
          <Link
            to={`/export/${statementId}`}
            className="text-sm text-indigo-400 hover:text-indigo-300"
          >
            Continue to export workflow →
          </Link>
        </>
      )}
    </div>
  )
}
