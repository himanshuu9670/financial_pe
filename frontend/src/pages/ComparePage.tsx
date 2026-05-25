import { useNavigate, useParams } from 'react-router-dom'
import { CompareWorkspace } from '@/components/workspace/CompareWorkspace'
import { UploadZone } from '@/components/pdf/UploadZone'
import { useAppStore } from '@/store/useAppStore'

export function ComparePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId

  if (!statementId) {
    return (
      <div className="p-8 max-w-lg mx-auto">
        <UploadZone onUploaded={(sid) => navigate(`/compare/${sid}`)} />
      </div>
    )
  }

  return <CompareWorkspace statementId={statementId} />
}
