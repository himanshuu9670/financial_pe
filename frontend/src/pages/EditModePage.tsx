import { motion } from 'framer-motion'
import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { EditModeExplorer } from '@/components/edit/EditModeExplorer'
import { Link } from 'react-router-dom'
import { UploadZone } from '@/components/pdf/UploadZone'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { usePdfStore } from '@/store/usePdfStore'

export function EditModePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId
  const setStatement = usePdfStore((s) => s.setStatement)

  useEffect(() => {
    if (statementId) {
      setStatement(statementId, '', statementsApi.previewUrl(statementId))
    }
  }, [statementId, setStatement])

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Financial Edit Mode</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Live recalculation with dependency propagation — PDF unchanged until export (Phase 5)
        </p>
      </motion.div>

      {!statementId ? (
        <UploadZone onUploaded={(sid) => navigate(`/edit/${sid}`)} />
      ) : (
        <>
          <EditModeExplorer statementId={statementId} />
          <p className="text-sm text-center">
            <Link
              to={`/export/${statementId}`}
              className="text-indigo-400 hover:text-indigo-300"
            >
              Continue to invisible PDF export →
            </Link>
          </p>
        </>
      )}
    </div>
  )
}
