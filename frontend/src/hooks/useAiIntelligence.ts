import { useQuery } from '@tanstack/react-query'
import { aiApi } from '@/services/aiApi'

export function useAiInsights(statementId: string | undefined, refresh = false) {
  return useQuery({
    queryKey: ['ai-insights', statementId, refresh],
    queryFn: () => aiApi.getInsights(statementId!, refresh),
    enabled: Boolean(statementId),
    staleTime: 15 * 60_000,
    gcTime: 30 * 60_000,
    refetchOnWindowFocus: false,
    placeholderData: (previous) => previous,
  })
}

export function useAiCategories(statementId: string | undefined) {
  return useQuery({
    queryKey: ['ai-categories', statementId],
    queryFn: () => aiApi.getCategories(statementId!),
    enabled: Boolean(statementId),
    staleTime: 15 * 60_000,
    gcTime: 30 * 60_000,
    refetchOnWindowFocus: false,
  })
}

export function useAiAnomalies(statementId: string | undefined) {
  return useQuery({
    queryKey: ['ai-anomalies', statementId],
    queryFn: () => aiApi.getAnomalies(statementId!),
    enabled: Boolean(statementId),
    staleTime: 15 * 60_000,
    refetchOnWindowFocus: false,
  })
}

export function useAiSuggestions(statementId: string | undefined, query?: string) {
  return useQuery({
    queryKey: ['ai-suggestions', statementId, query],
    queryFn: () => aiApi.getSuggestions(statementId!, query),
    enabled: Boolean(statementId),
  })
}

export function useAiStatus(statementId: string | undefined, pollWhileRunning = false) {
  return useQuery({
    queryKey: ['ai-status', statementId],
    queryFn: () => aiApi.getStatus(statementId!),
    enabled: Boolean(statementId),
    refetchInterval: (query) => {
      if (!pollWhileRunning) return false
      const st = query.state.data?.processing?.status
      return st === 'running' || st === 'queued' ? 2000 : false
    },
  })
}
