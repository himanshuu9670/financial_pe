export interface BankSignature {
  bank: string
  confidence: number
  layout_version: string
  signals: string[]
}

export interface TableRegion {
  page: number
  bbox: [number, number, number, number]
  row_count_estimate: number
  confidence: number
}

export interface ColumnDef {
  name: string
  x_min: number
  x_max: number
  x_center: number
}

export interface RowSegment {
  page: number
  row_index: number
  bbox: [number, number, number, number]
  text: string
  span_count: number
  confidence: number
}

export interface LayoutAnalysis {
  bank: BankSignature
  extraction_mode: string
  table_regions: TableRegion[]
  columns: ColumnDef[]
  header_row_y: number | null
  layout_confidence: number
  ocr_confidence: number | null
  is_scanned: boolean
  unknown_bank_adaptive: boolean
  warnings: string[]
}

export interface IntelligenceResponse {
  statement_id: string
  layout: LayoutAnalysis
  transaction_count: number
  layout_confidence: number
  ocr_confidence: number | null
  extraction_mode: string
  bank: string
  bank_confidence: number
  columns: ColumnDef[]
  table_regions: TableRegion[]
  row_segments: RowSegment[]
  warnings: string[]
  cached: boolean
}
