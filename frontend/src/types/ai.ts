export interface CategoryItem {
  transaction_id: string
  description: string
  category: string
  confidence: number
  signals: string[]
}

export interface AnomalyItem {
  transaction_id: string
  anomaly_type: string
  severity: 'low' | 'medium' | 'high'
  message: string
  score: number
  details?: Record<string, unknown>
}

export interface FraudAssessment {
  risk_score: number
  risk_level: string
  flags: string[]
  anomaly_count: number
}

export interface ConfidenceBreakdown {
  overall: number
  ocr?: number | null
  layout?: number | null
  financial?: number | null
  semantic?: number | null
  factors: string[]
}

export interface CategorySpend {
  category: string
  total_debit: number
  total_credit: number
  count: number
  percent_of_debit: number
}

export interface SmartSuggestion {
  id: string
  severity: string
  title: string
  message: string
  action?: string | null
  transaction_id?: string | null
}

export interface SmartCorrection {
  transaction_id?: string | null
  field: string
  original: string
  corrected: string
  confidence: number
  reason: string
}

export interface AiInsightsResponse {
  statement_id: string
  cached: boolean
  confidence: ConfidenceBreakdown
  fraud: FraudAssessment
  category_spend: CategorySpend[]
  spending_insight: Record<string, unknown>
  anomaly_count: number
  suggestion_count: number
  top_category: string | null
}

export interface AiCategoriesResponse {
  statement_id: string
  categories: CategoryItem[]
  cached: boolean
}

export interface AiAnomaliesResponse {
  statement_id: string
  anomalies: AnomalyItem[]
  fraud: FraudAssessment
  cached: boolean
}

export interface AiSuggestionsResponse {
  statement_id: string
  suggestions: SmartSuggestion[]
  corrections: SmartCorrection[]
  cached: boolean
}

export interface SemanticSearchResult {
  transaction_id: string
  score: number
  description: string
  category: string
}
