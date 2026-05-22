import { motion } from 'framer-motion'
import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ExportWorkflow } from '@/components/export/ExportWorkflow'
import { UploadZone } from '@/components/pdf/UploadZone'
import { useAppStore } from '@/store/useAppStore'

export function ExportPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId

  useEffect(() => {
    if (statementId) useAppStore.getState().setActiveStatementId(statementId)
  }, [statementId])

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Export PDF</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Invisible typography-preserving export — vector-safe targeted replacements
        </p>
      </motion.div>

      {!statementId ? (
        <UploadZone onUploaded={(sid) => navigate(`/export/${sid}`)} />
      ) : (
        <ExportWorkflow statementId={statementId} />
      )}
    </div>
  )
}
