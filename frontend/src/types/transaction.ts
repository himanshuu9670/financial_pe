export interface FieldCoordinate {
  text: string
  x: number
  y: number
  width: number
  height: number
  bbox: [number, number, number, number]
  font: string
  font_size: number
}

export interface TransactionCoordinates {
  date?: FieldCoordinate | null
  description?: FieldCoordinate | null
  debit?: FieldCoordinate | null
  credit?: FieldCoordinate | null
  balance?: FieldCoordinate | null
}

export interface ParsedTransaction {
  transaction_id: string
  page: number
  row_index: number
  date: string | null
  description: string
  debit: string | null
  credit: string | null
  balance: string | null
  coordinates: TransactionCoordinates
  font_metadata: Record<string, unknown>
  row_bbox: [number, number, number, number]
  confidence: number
  validation_warnings: string[]
}

export interface TransactionSummary {
  total_debit: string | number
  total_credit: string | number
  opening_balance: string | number | null
  closing_balance: string | number | null
  transaction_count: number
  validation_passed: boolean
  validation_issues: string[]
}

export interface ColumnDefinition {
  name: string
  x_min: number
  x_max: number
  x_center: number
}

export interface ParseDebugInfo {
  columns: ColumnDefinition[]
  grouped_row_count: number
  raw_row_count: number
  header_row_index: number | null
  extraction_mode?: string
  layout_confidence?: number | null
  ocr_confidence?: number | null
  header_row_y?: number | null
  bank_layout_version?: string | null
}

export interface TransactionsResponse {
  statement_id: string
  bank: string
  bank_confidence: number
  transactions: ParsedTransaction[]
  summary: TransactionSummary
  cached: boolean
  warnings: string[]
  debug?: ParseDebugInfo | null
  extraction_mode?: string
  layout_confidence?: number | null
  ocr_confidence?: number | null
}
