import { motion } from 'framer-motion'
import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { UploadZone } from '@/components/pdf/UploadZone'
import { TransactionExplorer } from '@/components/transactions/TransactionExplorer'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { usePdfStore } from '@/store/usePdfStore'
import { useTransactionStore } from '@/store/useTransactionStore'

export function TransactionsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId
  const setStatement = usePdfStore((s) => s.setStatement)

  useEffect(() => {
    if (statementId) {
      setStatement(statementId, '', statementsApi.previewUrl(statementId))
    }
    return () => useTransactionStore.getState().selectTransaction(null)
  }, [statementId, setStatement])

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Transaction Intelligence</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Structured transaction parsing with tight PDF-to-ledger sync and balance validation.
        </p>
      </motion.div>

      {!statementId ? (
        <UploadZone onUploaded={(sid) => navigate(`/transactions/${sid}`)} />
      ) : (
        <TransactionExplorer statementId={statementId} />
      )}
    </div>
  )
}
