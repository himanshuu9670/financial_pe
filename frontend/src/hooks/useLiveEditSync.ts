import { useCallback } from 'react'
import type { ChangeType, SessionStateResponse } from '@/types/editSession'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'

interface UseLiveEditSyncOptions {
  updateTransaction: (args: {
    transactionId: string
    field: ChangeType
    value: string | null
  }) => void
  state: SessionStateResponse | null
  setOptimisticState?: (state: SessionStateResponse) => void
}

/** Optimistic UI: flash affected rows when propagation runs. */
export function useLiveEditSync({
  updateTransaction,
  state,
}: UseLiveEditSyncOptions) {
  const flashTransactions = useWorkspaceStore((s) => s.flashTransactions)
  const markPropagation = useWorkspaceStore((s) => s.markPropagation)

  const updateWithSync = useCallback(
    (transactionId: string, field: ChangeType, value: string | null) => {
      updateTransaction({ transactionId, field, value })
      markPropagation()
    },
    [updateTransaction, markPropagation],
  )

  const onPropagationComplete = useCallback(
    (trace: SessionStateResponse['propagation_trace']) => {
      const ids = [...new Set(trace.map((t) => t.transaction_id))]
      if (ids.length) flashTransactions(ids)
    },
    [flashTransactions],
  )

  return { updateWithSync, onPropagationComplete, state }
}
