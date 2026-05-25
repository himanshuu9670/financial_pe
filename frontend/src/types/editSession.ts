export type ChangeType = 'debit' | 'credit' | 'balance' | 'description' | 'date'

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

export interface LedgerEntry {
  transaction_id: string
  row_index: number
  page: number
  date: string | null
  description: string
  debit: string | number | null
  credit: string | number | null
  balance: string | number | null
  previous_balance: string | number | null
  is_modified: boolean
  propagation_affected: boolean
  validation_warnings: string[]
  row_bbox: number[]
  coordinates?: TransactionCoordinates | null
  font_metadata?: Record<string, unknown>
}

export interface SummarySchema {
  total_debit: string | number
  total_credit: string | number
  opening_balance: string | number | null
  closing_balance: string | number | null
  transaction_count: number
  validation_passed: boolean
  validation_issues: string[]
}

export interface PropagationTrace {
  transaction_id: string
  field: string
  old_value: string | null
  new_value: string | null
  reason: string
}

export interface DependencyNode {
  transaction_id: string
  index: number
  previous_id: string | null
  next_id: string | null
}

export interface EditTimelineEvent {
  operation_id: string
  timestamp: string
  action: string
  description: string
  transaction_id: string | null
  field: string | null
}

export interface SessionStateResponse {
  session_id: string
  statement_id: string
  bank: string
  entries: LedgerEntry[]
  summary: SummarySchema
  validation_passed: boolean
  validation_issues: string[]
  modified_count: number
  can_undo: boolean
  can_redo: boolean
  propagation_trace: PropagationTrace[]
  dependency_graph: DependencyNode[]
  edit_timeline?: EditTimelineEvent[]
  debug?: Record<string, unknown> | null
}

export type EditableField = 'debit' | 'credit' | 'balance'
