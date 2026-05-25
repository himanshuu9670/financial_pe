import type { RenderPageProps } from '@react-pdf-viewer/core'
import type { ReactElement } from 'react'
import type { IntelligenceResponse } from '@/types/intelligence'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { cn } from '@/utils/cn'

interface LayoutIntelligenceOverlayProps {
  pageIndex: number
  scale: number
  pageWidth: number
  pageHeight: number
  intelligence: IntelligenceResponse | undefined
  showTables?: boolean
  showColumns?: boolean
  showRows?: boolean
}

export function LayoutIntelligenceOverlay({
  pageIndex,
  scale,
  pageWidth,
  pageHeight,
  intelligence,
  showTables = true,
  showColumns = true,
  showRows = true,
}: LayoutIntelligenceOverlayProps) {
  if (!intelligence) return null

  const pageNum = pageIndex + 1
  const tables = intelligence.table_regions.filter((t) => t.page === pageNum)
  const columns = intelligence.columns
  const rows = intelligence.row_segments.filter((r) => r.page === pageNum)

  return (
    <div
      className="absolute inset-0 pointer-events-none z-25"
      style={{ width: pageWidth * scale, height: pageHeight * scale }}
    >
      {showTables &&
        tables.map((t, i) => {
          const rect = pdfBboxToViewport(t.bbox, scale)
          return (
            <div
              key={`table-${i}`}
              className="absolute border-2 border-amber-400/60 bg-amber-400/5 rounded"
              style={{
                left: rect.left,
                top: rect.top,
                width: rect.width,
                height: rect.height,
              }}
              title={`Table ~${t.row_count_estimate} rows (${(t.confidence * 100).toFixed(0)}%)`}
            />
          )
        })}

      {showColumns &&
        columns.map((col, i) => (
          <div
            key={`intel-col-${i}`}
            className="absolute top-0 bottom-0 border-l-2 border-dashed border-violet-400/50"
            style={{ left: col.x_min * scale }}
            title={col.name}
          />
        ))}

      {showRows &&
        rows.map((r) => {
          if (!r.bbox || r.bbox.length < 4) return null
          const rect = pdfBboxToViewport(r.bbox, scale)
          return (
            <div
              key={`seg-${r.row_index}`}
              className={cn(
                'absolute border border-sky-400/30 bg-sky-400/5',
                r.confidence < 0.6 && 'border-orange-400/50 bg-orange-400/10',
              )}
              style={{
                left: rect.left,
                top: rect.top,
                width: rect.width,
                height: Math.max(rect.height, 8),
              }}
              title={`Row ${r.row_index} · ${(r.confidence * 100).toFixed(0)}%`}
            />
          )
        })}
    </div>
  )
}

export function renderPageWithIntelligence(
  intelligence: IntelligenceResponse | undefined,
  options: { showTables?: boolean; showColumns?: boolean; showRows?: boolean },
) {
  return function renderPage(props: RenderPageProps): ReactElement {
    const { pageIndex, scale, width, height, canvasLayer, textLayer, annotationLayer } = props
    return (
      <>
        {canvasLayer.children}
        {textLayer.children}
        {annotationLayer.children}
        <LayoutIntelligenceOverlay
          pageIndex={pageIndex}
          scale={scale}
          pageWidth={width}
          pageHeight={height}
          intelligence={intelligence}
          showTables={options.showTables}
          showColumns={options.showColumns}
          showRows={options.showRows}
        />
      </>
    )
  }
}
