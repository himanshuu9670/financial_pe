import type { RenderPageProps } from '@react-pdf-viewer/core'
import { useMemo, type ReactElement } from 'react'
import type { PageExtraction, TextSpan } from '@/types/extraction'
import { usePdfStore } from '@/store/usePdfStore'
import { blockLabel, pdfBboxToViewport } from '@/utils/coordinates'
import { cn } from '@/utils/cn'

interface ExtractionOverlayProps {
  pageIndex: number
  scale: number
  pageData?: PageExtraction
  enabled?: boolean
}

function spanId(page: number, bi: number, si: number) {
  return `${page}-${bi}-${si}`
}

export function ExtractionOverlay({ pageIndex, scale, pageData, enabled }: ExtractionOverlayProps) {
  const showOverlayStore = usePdfStore((s) => s.showOverlay)
  const showOverlay = enabled ?? showOverlayStore
  const hoveredSpanId = usePdfStore((s) => s.hoveredSpanId)
  const selectedSpan = usePdfStore((s) => s.selectedSpan)
  const setHoveredSpanId = usePdfStore((s) => s.setHoveredSpanId)
  const setSelectedSpan = usePdfStore((s) => s.setSelectedSpan)

  const spans = useMemo(() => {
    if (!pageData) return []
    const out: { span: TextSpan; id: string; blockIdx: number }[] = []
    pageData.blocks.forEach((block, bi) => {
      block.spans.forEach((span, si) => {
        if (span.text.trim()) out.push({ span, id: spanId(pageIndex + 1, bi, si), blockIdx: bi })
      })
    })
    return out
  }, [pageData, pageIndex])

  if (!showOverlay || !pageData) return null

  return (
    <div
      className="absolute inset-0 pointer-events-none"
      style={{ width: pageData.width * scale, height: pageData.height * scale }}
    >
      {spans.map(({ span, id }) => {
        const rect = pdfBboxToViewport(span.bbox, scale)
        const isHovered = hoveredSpanId === id
        const isSelected =
          selectedSpan?.text === span.text &&
          selectedSpan?.x === span.x &&
          selectedSpan?.y === span.y

        return (
          <div
            key={id}
            role="button"
            tabIndex={0}
            className={cn(
              'absolute pointer-events-auto border transition-colors cursor-crosshair',
              isSelected
                ? 'border-cyan-400 bg-cyan-400/25 z-20'
                : isHovered
                  ? 'border-indigo-400 bg-indigo-400/20 z-10'
                  : 'border-indigo-500/30 bg-indigo-500/5 hover:border-indigo-400/60',
            )}
            style={{
              left: rect.left,
              top: rect.top,
              width: rect.width,
              height: Math.max(rect.height, 8),
            }}
            title={blockLabel(span)}
            onMouseEnter={() => setHoveredSpanId(id)}
            onMouseLeave={() => setHoveredSpanId(null)}
            onClick={() => setSelectedSpan(span)}
          />
        )
      })}
    </div>
  )
}

export function renderPageWithOverlay(
  pageDataByIndex: Map<number, PageExtraction>,
): (props: RenderPageProps) => ReactElement {
  return (props: RenderPageProps) => {
    const pageNum = props.pageIndex + 1
    const pageData = pageDataByIndex.get(pageNum)

    return (
      <>
        {props.canvasLayer.children}
        <div className="relative" style={{ width: props.width, height: props.height }}>
          {props.textLayer.children}
          <ExtractionOverlay pageIndex={props.pageIndex} scale={props.scale} pageData={pageData} />
        </div>
        {props.annotationLayer.children}
      </>
    )
  }
}
