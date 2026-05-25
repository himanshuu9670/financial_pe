import { apiClient } from '@/services/api'
import type {
  AiAnomaliesResponse,
  AiCategoriesResponse,
  AiInsightsResponse,
  AiSuggestionsResponse,
  SemanticSearchResult,
} from '@/types/ai'
import type { ConfidenceBreakdown, SmartCorrection } from '@/types/ai'

export const aiApi = {
  getInsights: (statementId: string, refresh = false) =>
    apiClient
      .get<AiInsightsResponse>('/ai/insights', {
        params: { statement_id: statementId, refresh },
      })
      .then((r) => r.data),

  getCategories: (statementId: string, refresh = false) =>
    apiClient
      .get<AiCategoriesResponse>('/ai/categories', {
        params: { statement_id: statementId, refresh },
      })
      .then((r) => r.data),

  getAnomalies: (statementId: string, refresh = false) =>
    apiClient
      .get<AiAnomaliesResponse>('/ai/anomalies', {
        params: { statement_id: statementId, refresh },
      })
      .then((r) => r.data),

  getConfidence: (statementId: string, refresh = false) =>
    apiClient
      .get<{ statement_id: string; confidence: ConfidenceBreakdown; corrections: SmartCorrection[]; cached: boolean }>(
        '/ai/confidence',
        { params: { statement_id: statementId, refresh } },
      )
      .then((r) => r.data),

  getSuggestions: (statementId: string, query?: string) =>
    apiClient
      .post<AiSuggestionsResponse>(
        '/ai/suggestions',
        { query: query ?? null },
        { params: { statement_id: statementId } },
      )
      .then((r) => r.data),

  semanticSearch: (statementId: string, q: string, limit = 20) =>
    apiClient
      .get<{ statement_id: string; query: string; results: SemanticSearchResult[] }>(
        '/ai/search',
        { params: { statement_id: statementId, q, limit } },
      )
      .then((r) => r.data),

  triggerAnalyze: (statementId: string, asyncMode = false) =>
    apiClient
      .post<{ status: string; confidence?: number; anomaly_count?: number }>(
        `/ai/analyze/${statementId}`,
        null,
        { params: { async_mode: asyncMode } },
      )
      .then((r) => r.data),

  getStatus: (statementId: string) =>
    apiClient
      .get<{
        statement_id: string
        processing: { status: string; updated_at?: string }
        has_report: boolean
        embeddings_cached: boolean
        analyzed_at?: string
      }>('/ai/status', { params: { statement_id: statementId } })
      .then((r) => r.data),
}
