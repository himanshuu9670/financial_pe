import { useQuery } from '@tanstack/react-query'
import { statementsApi } from '@/services/api'
import { usePdfStore } from '@/store/usePdfStore'
import { useEffect } from 'react'

export function usePdfExtraction(statementId: string | undefined, enabled = true) {
  const setExtraction = usePdfStore((s) => s.setExtraction)
  const setExtractionLoading = usePdfStore((s) => s.setExtractionLoading)
  const setExtractionError = usePdfStore((s) => s.setExtractionError)

  const query = useQuery({
    queryKey: ['extraction', statementId],
    queryFn: () => statementsApi.extract(statementId!).then((r) => r.data),
    enabled: Boolean(statementId) && enabled,
    staleTime: 30 * 60_000,
    gcTime: 60 * 60_000,
    refetchOnWindowFocus: false,
    placeholderData: (previous) => previous,
  })

  useEffect(() => {
    setExtractionLoading(query.isLoading || query.isFetching)
  }, [query.isLoading, query.isFetching, setExtractionLoading])

  useEffect(() => {
    if (query.data) setExtraction(query.data)
  }, [query.data, setExtraction])

  useEffect(() => {
    if (query.error) {
      const msg =
        (query.error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? 'Extraction failed'
      setExtractionError(String(msg))
    } else if (!query.isLoading) {
      setExtractionError(null)
    }
  }, [query.error, query.isLoading, setExtractionError])

  return query
}
