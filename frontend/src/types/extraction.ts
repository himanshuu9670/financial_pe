export interface TextSpan {
  text: string
  x: number
  y: number
  width: number
  height: number
  font: string
  font_size: number
  bbox: [number, number, number, number]
  flags?: number
  color?: number
}

export interface TextBlock {
  text: string
  x: number
  y: number
  width: number
  height: number
  font: string
  font_size: number
  bbox: [number, number, number, number]
  spans: TextSpan[]
}

export interface PageExtraction {
  page: number
  width: number
  height: number
  blocks: TextBlock[]
}

export interface DocumentExtraction {
  statement_id?: string
  total_pages: number
  pages: PageExtraction[]
  span_count: number
  block_count: number
  warnings: string[]
  is_likely_scanned: boolean
  cached?: boolean
  processing_status?: string
}
