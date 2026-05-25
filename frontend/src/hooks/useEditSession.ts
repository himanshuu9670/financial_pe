import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { editApi } from '@/services/editApi'
import { useEditSessionStore } from '@/store/useEditSessionStore'
import type { ChangeType } from '@/types/editSession'

export function useEditSession(statementId: string | undefined) {
  const sessionId = useEditSessionStore((s) => s.sessionId)
  const activeStatementId = useEditSessionStore((s) => s.statementId)
  const setSession = useEditSessionStore((s) => s.setSession)
  const setState = useEditSessionStore((s) => s.setState)
  const setLoading = useEditSessionStore((s) => s.setLoading)
  const setError = useEditSessionStore((s) => s.setError)
  const debugMode = useEditSessionStore((s) => s.debugMode)
  const queryClient = useQueryClient()

  const startMutation = useMutation({
    mutationFn: () => editApi.startSession(statementId!).then((r) => r.data),
    onSuccess: (data) => {
      setSession(data.session_id, data.statement_id)
      queryClient.invalidateQueries({ queryKey: ['edit-session', data.session_id] })
    },
  })

  useEffect(() => {
    // If there's no active session, or the active session belongs to a different
    // statement than the one requested, clear and start a new edit session.
    if (!statementId) return

    const needsNewSession =
      !sessionId || (activeStatementId != null && activeStatementId !== statementId)

    if (needsNewSession && !startMutation.isPending && !startMutation.isSuccess) {
      // Clear any stale session state so the new session starts cleanly
      if (sessionId) useEditSessionStore.getState().clear()
      startMutation.mutate()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statementId, sessionId, activeStatementId])

  const stateQuery = useQuery({
    queryKey: ['edit-session', sessionId, debugMode],
    queryFn: () => editApi.getSessionState(sessionId!, debugMode).then((r) => r.data),
    enabled: Boolean(sessionId),
    refetchOnWindowFocus: false,
  })

  useEffect(() => {
    if (stateQuery.data) setState(stateQuery.data)
  }, [stateQuery.data, setState])

  useEffect(() => {
    setLoading(startMutation.isPending || stateQuery.isLoading || stateQuery.isFetching)
  }, [startMutation.isPending, stateQuery.isLoading, stateQuery.isFetching, setLoading])

  useEffect(() => {
    const err = startMutation.error || stateQuery.error
    if (err) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Edit session error'
      setError(String(msg))
    } else if (!startMutation.isPending && !stateQuery.isLoading) {
      setError(null)
    }
  }, [startMutation.error, stateQuery.error, startMutation.isPending, stateQuery.isLoading, setError])

  const updateMutation = useMutation({
    mutationFn: ({
      transactionId,
      field,
      value,
    }: {
      transactionId: string
      field: ChangeType
      value: string | null
    }) =>
      editApi
        .updateTransaction(sessionId!, transactionId, field, value)
        .then((r) => r.data.state),
    onSuccess: (state) => setState(state),
  })

  const undoMutation = useMutation({
    mutationFn: () => editApi.undo(sessionId!).then((r) => r.data),
    onSuccess: (state) => setState(state),
  })

  const redoMutation = useMutation({
    mutationFn: () => editApi.redo(sessionId!).then((r) => r.data),
    onSuccess: (state) => setState(state),
  })

  const commitMutation = useMutation({
    mutationFn: (notes?: string) => editApi.commit(sessionId!, notes).then((r) => r.data),
    onSuccess: (state) => setState(state),
  })

  return {
    sessionId,
    state: useEditSessionStore((s) => s.state),
    loading: useEditSessionStore((s) => s.loading),
    error: useEditSessionStore((s) => s.error),
    updateTransaction: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
    undo: () => undoMutation.mutate(),
    redo: () => redoMutation.mutate(),
    commit: (notes?: string) => commitMutation.mutate(notes),
    // Async variant for callers that need to await commit completion
    commitAsync: (notes?: string) => commitMutation.mutateAsync(notes),
    canUndo: stateQuery.data?.can_undo ?? false,
    canRedo: stateQuery.data?.can_redo ?? false,
    isCommitting: commitMutation.isPending,
  }
}
