import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { statementsApi } from '@/services/api'
import { useTransactionStore } from '@/store/useTransactionStore'

export function useTransactions(statementId: string | undefined, debug = false) {
  const setData = useTransactionStore((s) => s.setData)
  const setLoading = useTransactionStore((s) => s.setLoading)
  const setError = useTransactionStore((s) => s.setError)

  const query = useQuery({
    queryKey: ['transactions', statementId, debug],
    queryFn: () =>
      statementsApi
        .transactions(statementId!, { debug })
        .then((r) => r.data),
    enabled: Boolean(statementId),
    staleTime: 10 * 60_000,
  })

  useEffect(() => {
    setLoading(query.isLoading || query.isFetching)
  }, [query.isLoading, query.isFetching, setLoading])

  useEffect(() => {
    if (query.data) setData(query.data)
  }, [query.data, setData])

  useEffect(() => {
    if (query.error) {
      const msg =
        (query.error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? 'Failed to parse transactions'
      setError(String(msg))
    } else if (!query.isLoading) {
      setError(null)
    }
  }, [query.error, query.isLoading, setError])

  return query
}
