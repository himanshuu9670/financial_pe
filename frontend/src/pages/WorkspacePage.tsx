import { useNavigate, useParams } from 'react-router-dom'
import { UploadZone } from '@/components/pdf/UploadZone'
import { EditingWorkspace } from '@/components/workspace/EditingWorkspace'
import { useAppStore } from '@/store/useAppStore'

export function WorkspacePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId

  if (!statementId) {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <h1 className="text-xl font-bold mb-2">Enterprise Editing Workspace</h1>
        <p className="text-sm text-zinc-500 mb-6">
          Upload a statement to open the real-time PDF ↔ ledger workspace.
        </p>
        <UploadZone onUploaded={(sid) => navigate(`/workspace/${sid}`)} />
      </div>
    )
  }

  return <EditingWorkspace statementId={statementId} />
}
