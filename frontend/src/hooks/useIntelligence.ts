import { useQuery } from '@tanstack/react-query'
import { intelligenceApi } from '@/services/intelligenceApi'

export function useIntelligence(
  statementId: string | undefined,
  options?: { refresh?: boolean; forceOcr?: boolean },
) {
  return useQuery({
    queryKey: ['intelligence', statementId, options?.refresh, options?.forceOcr],
    queryFn: async () => {
      if (!statementId) throw new Error('No statement id')
      const { data } = await intelligenceApi.analyze(statementId, {
        refresh: options?.refresh,
        force_ocr: options?.forceOcr,
      })
      return data
    },
    enabled: !!statementId,
    staleTime: 60_000,
  })
}
