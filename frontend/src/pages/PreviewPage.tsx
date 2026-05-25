import { motion } from 'framer-motion'
import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { UploadZone } from '@/components/pdf/UploadZone'
import { StatementPdfViewer } from '@/components/pdf/StatementPdfViewer'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { usePdfStore } from '@/store/usePdfStore'

export function PreviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId
  const setStatement = usePdfStore((s) => s.setStatement)
  const fileUrl = usePdfStore((s) => s.fileUrl)

  useEffect(() => {
    if (statementId && (!fileUrl || usePdfStore.getState().statementId !== statementId)) {
      setStatement(statementId, '', statementsApi.previewUrl(statementId))
    }
  }, [statementId, fileUrl, setStatement])

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">PDF Preview & Extraction</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Review the PDF preview and extracted statement metadata with overlay controls.
        </p>
      </motion.div>

      {!statementId ? (
        <UploadZone />
      ) : (
        <>
          <StatementPdfViewer statementId={statementId} />
          <div className="flex justify-center">
            <button
              type="button"
              onClick={() => {
                usePdfStore.getState().clearStatement()
                navigate('/preview')
              }}
              className="text-sm text-zinc-500 hover:text-zinc-300"
            >
              Upload another statement
            </button>
          </div>
        </>
      )}
    </div>
  )
}
