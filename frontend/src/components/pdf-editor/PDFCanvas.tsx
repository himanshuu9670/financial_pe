import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import { pageNavigationPlugin } from '@react-pdf-viewer/page-navigation'
import type { RenderPageProps } from '@react-pdf-viewer/core'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { useCallback, useMemo, useRef, type ReactElement } from 'react'
import type { ChangeType, LedgerEntry, SessionStateResponse } from '@/types/editSession'
import { OverlayEditor } from '@/components/pdf-editor/OverlayEditor'
import { SelectionLayer } from '@/components/pdf-editor/SelectionLayer'
import { HighlightLayer } from '@/components/pdf-editor/HighlightLayer'
import { LivePreviewLayer } from '@/components/pdf-editor/LivePreviewLayer'
import { CoordinateLayer } from '@/components/pdf-editor/CoordinateLayer'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import { fieldValue, getFieldCoordinate } from '@/utils/workspace'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

interface PDFCanvasProps {
  fileUrl: string
  state: SessionStateResponse
  onFieldCommit: (transactionId: string, field: ChangeType, value: string | null) => void
  onPageJump?: (pageIndex: number) => void
}

export function PDFCanvas({ fileUrl, state, onFieldCommit, onPageJump }: PDFCanvasProps) {
  const pdfEditTarget = useWorkspaceStore((s) => s.pdfEditTarget)
  const setPdfEditTarget = useWorkspaceStore((s) => s.setPdfEditTarget)
  const selectTransaction = useTransactionStore((s) => s.selectTransaction)

  const jumpRef = useRef<(i: number) => void>(() => {})
  const pageNav = pageNavigationPlugin()
  jumpRef.current = pageNav.jumpToPage

  const layoutPlugin = defaultLayoutPlugin({ sidebarTabs: () => [] })

  const handleFieldClick = useCallback(
    (entry: LedgerEntry, field: ChangeType) => {
      const coord = getFieldCoordinate(entry, field)
      if (!coord?.bbox) return
      setPdfEditTarget({
        transactionId: entry.transaction_id,
        field,
        page: entry.page,
        bbox: coord.bbox,
        fontSize: coord.font_size,
        font: coord.font,
      })
      selectTransaction(entry.transaction_id)
      jumpRef.current(entry.page - 1)
      onPageJump?.(entry.page - 1)
    },
    [setPdfEditTarget, selectTransaction, onPageJump],
  )

  const renderPage = useMemo(() => {
    return function render(props: RenderPageProps): ReactElement {
      const { pageIndex, scale, width, height, canvasLayer, textLayer, annotationLayer } = props
      const pageNum = pageIndex + 1
      const entries = state.entries

      const editingOnPage =
        pdfEditTarget && pdfEditTarget.page === pageNum ? pdfEditTarget : null

      return (
        <>
          {canvasLayer.children}
          <div
            className="relative"
            style={{ width, height }}
          >
            {textLayer.children}
            <div className="absolute inset-0" style={{ width, height }}>
              <SelectionLayer
                pageIndex={pageIndex}
                scale={scale}
                entries={entries}
                onFieldClick={handleFieldClick}
              />
              <HighlightLayer pageIndex={pageIndex} scale={scale} entries={entries} />
              <LivePreviewLayer pageIndex={pageIndex} scale={scale} entries={entries} />
              <CoordinateLayer pageIndex={pageIndex} scale={scale} entries={entries} />
              {editingOnPage && (
                <OverlayEditor
                  bbox={editingOnPage.bbox}
                  scale={scale}
                  initialValue={fieldValue(
                    entries.find((e) => e.transaction_id === editingOnPage.transactionId)!,
                    editingOnPage.field,
                  )}
                  field={editingOnPage.field}
                  onCommit={(val) => {
                    onFieldCommit(editingOnPage.transactionId, editingOnPage.field, val)
                    setPdfEditTarget(null)
                  }}
                  onCancel={() => setPdfEditTarget(null)}
                />
              )}
            </div>
          </div>
          {annotationLayer.children}
        </>
      )
    }
  }, [state.entries, pdfEditTarget, onFieldCommit, setPdfEditTarget])

  return (
    <div className="h-full min-h-[480px] rounded-xl overflow-hidden glass border border-white/10">
      <Worker workerUrl={WORKER_URL}>
        <Viewer fileUrl={fileUrl} plugins={[layoutPlugin, pageNav]} renderPage={renderPage} />
      </Worker>
    </div>
  )
}
