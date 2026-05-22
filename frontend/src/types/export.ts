export interface ApplyEditsRequest {
  statement_id: string
  session_id?: string | null
  validate_visual?: boolean
}

export interface VisualValidation {
  text_match_ratio: number
  bbox_overlap_ratio: number
  regions_checked: number
  issues: string[]
  passed: boolean
}

export interface ApplyEditsResponse {
  statement_id: string
  status: string
  download_url: string
  original_preview_url: string
  edited_preview_url: string
  replacements_applied: number
  replacements_failed: number
  validation: VisualValidation
  warnings: string[]
}
