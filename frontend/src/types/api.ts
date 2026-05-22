export interface Statement {
  id: string
  user_id: string
  bank_name: string | null
  account_number: string | null
  original_filename: string
  original_pdf_path: string
  edited_pdf_path: string | null
  preview_path: string | null
  version: number
  status: string
  opening_balance: string | null
  closing_balance: string | null
  page_count: number | null
  file_size_bytes?: number | null
  processing_error?: string | null
  extracted_at?: string | null
  created_at: string
  updated_at: string
}

export interface StatementListResponse {
  items: Statement[]
  total: number
}

export interface UploadResponse {
  statement_id: string
  filename: string
  status: string
  message: string
  file_size_bytes?: number
  page_count?: number
  storage_path?: string
}

export interface HealthResponse {
  status: string
  app: string
  database: boolean
  redis: boolean
  timestamp: string
}
