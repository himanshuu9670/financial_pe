import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { AlertTriangle, Eye, EyeOff, Loader2, RefreshCw } from 'lucide-react'
import { useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { GlassCard } from '@/components/ui/GlassCard'
import { renderPageWithOverlay } from '@/components/pdf/ExtractionOverlay'
import { usePdfExtraction } from '@/hooks/usePdfExtraction'
import { statementsApi } from '@/services/api'
import { usePdfStore } from '@/store/usePdfStore'
import type { PageExtraction } from '@/types/extraction'
import { cn } from '@/utils/cn'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

interface StatementPdfViewerProps {
  statementId: string
}

export function StatementPdfViewer({ statementId }: StatementPdfViewerProps) {
  const queryClient = useQueryClient()
  const fileUrl = usePdfStore((s) => s.fileUrl) ?? statementsApi.previewUrl(statementId)
  const showOverlay = usePdfStore((s) => s.showOverlay)
  const setShowOverlay = usePdfStore((s) => s.setShowOverlay)
  const extraction = usePdfStore((s) => s.extraction)
  const extractionLoading = usePdfStore((s) => s.extractionLoading)
  const extractionError = usePdfStore((s) => s.extractionError)
  const selectedSpan = usePdfStore((s) => s.selectedSpan)
  const hoveredSpanId = usePdfStore((s) => s.hoveredSpanId)

  const { refetch, isFetching } = usePdfExtraction(statementId)

  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: () => [],
  })

  const pageDataByIndex = useMemo(() => {
    const map = new Map<number, PageExtraction>()
    extraction?.pages.forEach((p) => map.set(p.page, p))
    return map
  }, [extraction])

  const renderPage = useMemo(
    () => renderPageWithOverlay(pageDataByIndex),
    [pageDataByIndex],
  )

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => setShowOverlay(!showOverlay)}
          className={cn(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-colors',
            showOverlay
              ? 'border-indigo-500/50 bg-indigo-500/20 text-indigo-300'
              : 'border-white/10 text-zinc-400 hover:text-zinc-200',
          )}
        >
          {showOverlay ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          Overlay {showOverlay ? 'on' : 'off'}
        </button>

        <button
          type="button"
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['extraction', statementId] })
            refetch()
          }}
          disabled={isFetching}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border border-white/10 text-zinc-400 hover:text-zinc-200 disabled:opacity-50"
        >
          <RefreshCw className={cn('w-4 h-4', isFetching && 'animate-spin')} />
          Re-extract
        </button>

        {extraction && (
          <span className="text-xs text-zinc-500">
            {extraction.span_count} spans · {extraction.block_count} blocks
            {extraction.cached && ' · cached'}
          </span>
        )}

        {extractionLoading && (
          <span className="inline-flex items-center gap-1 text-xs text-indigo-400">
            <Loader2 className="w-3 h-3 animate-spin" />
            Extracting coordinates…
          </span>
        )}
      </div>

      {extraction?.is_likely_scanned && (
        <div className="flex items-center gap-2 text-amber-400 text-sm glass rounded-lg px-4 py-2 border border-amber-500/20">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          Scanned PDF detected — OCR required for full extraction (future phase).
        </div>
      )}

      {extraction?.warnings.map((w) => (
        <p key={w} className="text-xs text-amber-500/80">
          {w}
        </p>
      ))}

      {extractionError && (
        <p className="text-sm text-red-400">{extractionError}</p>
      )}

      <div className="grid lg:grid-cols-4 gap-4">
        <GlassCard className="lg:col-span-3 p-0 overflow-hidden min-h-[600px] [&_.rpv-core__viewer]:min-h-[580px]">
          <Worker workerUrl={WORKER_URL}>
            <Viewer
              fileUrl={fileUrl}
              plugins={[defaultLayoutPluginInstance]}
              renderPage={renderPage}
            />
          </Worker>
        </GlassCard>

        <GlassCard className="lg:col-span-1 text-sm space-y-3 max-h-[640px] overflow-y-auto">
          <h3 className="font-semibold text-zinc-300">Span inspector</h3>
          {selectedSpan ? (
            <dl className="space-y-2 text-xs font-mono text-zinc-400">
              <div>
                <dt className="text-zinc-600">Text</dt>
                <dd className="text-zinc-200 break-all">{selectedSpan.text}</dd>
              </div>
              <div>
                <dt className="text-zinc-600">Font</dt>
                <dd>
                  {selectedSpan.font} · {selectedSpan.font_size}pt
                </dd>
              </div>
              <div>
                <dt className="text-zinc-600">Position</dt>
                <dd>
                  x={selectedSpan.x} y={selectedSpan.y}
                </dd>
              </div>
              <div>
                <dt className="text-zinc-600">BBox</dt>
                <dd>[{selectedSpan.bbox.join(', ')}]</dd>
              </div>
            </dl>
          ) : (
            <p className="text-zinc-500 text-xs">
              {hoveredSpanId
                ? 'Click a highlighted span to inspect typography metadata.'
                : 'Enable overlay and hover spans to debug extraction.'}
            </p>
          )}

          {extraction && (
            <div className="pt-3 border-t border-white/10">
              <p className="text-xs text-zinc-600 mb-2">Pages extracted</p>
              <p className="text-zinc-400">{extraction.pages.map((p) => p.page).join(', ')}</p>
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  )
}
