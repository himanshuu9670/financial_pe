import type { RenderPageProps } from '@react-pdf-viewer/core'
import type { ReactElement } from 'react'
import type { PageExtraction } from '@/types/extraction'
import type { ParsedTransaction } from '@/types/transaction'
import { useTransactionStore } from '@/store/useTransactionStore'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { cn } from '@/utils/cn'
import { ExtractionOverlay } from '@/components/pdf/ExtractionOverlay'

interface TransactionOverlayProps {
  pageIndex: number
  scale: number
  pageWidth: number
  pageHeight: number
  transactions: ParsedTransaction[]
}

export function TransactionOverlay({
  pageIndex,
  scale,
  pageWidth,
  pageHeight,
  transactions,
}: TransactionOverlayProps) {
  const showRowBboxes = useTransactionStore((s) => s.showRowBboxes)
  const selectedId = useTransactionStore((s) => s.selectedTransactionId)
  const hoveredId = useTransactionStore((s) => s.hoveredTransactionId)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)
  const hoverTransaction = useTransactionStore((s) => s.hoverTransaction)
  const showColumnGuides = useTransactionStore((s) => s.showColumnGuides)
  const debug = useTransactionStore((s) => s.debugMode)
  const columns = useTransactionStore((s) => s.data?.debug?.columns ?? [])

  const pageNum = pageIndex + 1
  const pageTxns = transactions.filter((t) => t.page === pageNum)

  if (!showRowBboxes && !showColumnGuides) return null

  return (
    <div
      className="absolute inset-0 pointer-events-none z-30"
      style={{ width: pageWidth * scale, height: pageHeight * scale }}
    >
      {debug &&
        showColumnGuides &&
        columns.map((col, i) => (
          <div
            key={`col-${i}`}
            className="absolute top-0 bottom-0 border-l border-dashed border-purple-500/40"
            style={{ left: col.x_min * scale, width: (col.x_max - col.x_min) * scale }}
            title={col.name}
          />
        ))}

      {showRowBboxes &&
        pageTxns.map((txn) => {
          if (!txn.row_bbox || txn.row_bbox.length < 4) return null
          const rect = pdfBboxToViewport(txn.row_bbox, scale)
          const isSelected = selectedId === txn.transaction_id
          const isHovered = hoveredId === txn.transaction_id

          return (
            <div
              key={txn.transaction_id}
              role="button"
              tabIndex={0}
              className={cn(
                'absolute pointer-events-auto border-2 transition-all cursor-pointer rounded-sm',
                isSelected
                  ? 'border-cyan-400 bg-cyan-400/20 shadow-[0_0_20px_rgba(34,211,238,0.4)]'
                  : isHovered
                    ? 'border-emerald-400/80 bg-emerald-400/15'
                    : 'border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-400/60',
              )}
              style={{
                left: rect.left,
                top: rect.top,
                width: rect.width,
                height: Math.max(rect.height, 10),
              }}
              title={`${txn.date ?? ''} ${txn.description.slice(0, 60)}`}
              onMouseEnter={() => hoverTransaction(txn.transaction_id)}
              onMouseLeave={() => hoverTransaction(null)}
              onClick={() => selectTransaction(txn.transaction_id)}
            />
          )
        })}
    </div>
  )
}

export function renderPageWithLayers(
  pageDataByIndex: Map<number, PageExtraction>,
  transactions: ParsedTransaction[],
  showSpanOverlay: boolean,
): (props: RenderPageProps) => ReactElement {
  return (props: RenderPageProps) => {
    const pageNum = props.pageIndex + 1
    const pageData = pageDataByIndex.get(pageNum)
    const pageWidth = pageData?.width ?? props.width
    const pageHeight = pageData?.height ?? props.height

    return (
      <>
        {props.canvasLayer.children}
        <div className="relative" style={{ width: props.width, height: props.height }}>
          {props.textLayer.children}
          {showSpanOverlay && (
            <ExtractionOverlay
              pageIndex={props.pageIndex}
              scale={props.scale}
              pageData={pageData}
              enabled
            />
          )}
          <TransactionOverlay
            pageIndex={props.pageIndex}
            scale={props.scale}
            pageWidth={pageWidth}
            pageHeight={pageHeight}
            transactions={transactions}
          />
        </div>
        {props.annotationLayer.children}
      </>
    )
  }
}
