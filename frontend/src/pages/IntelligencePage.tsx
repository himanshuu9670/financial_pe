import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { motion } from 'framer-motion'
import { Brain, RefreshCw } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { IntelligenceDebugPanel } from '@/components/intelligence/IntelligenceDebugPanel'
import { renderPageWithIntelligence } from '@/components/intelligence/LayoutIntelligenceOverlay'
import { UploadZone } from '@/components/pdf/UploadZone'
import { useIntelligence } from '@/hooks/useIntelligence'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/utils/cn'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

export function IntelligencePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const activeId = useAppStore((s) => s.activeStatementId)
  const statementId = id ?? activeId

  const [refresh, setRefresh] = useState(false)
  const [forceOcr, setForceOcr] = useState(false)
  const [showTables, setShowTables] = useState(true)
  const [showColumns, setShowColumns] = useState(true)
  const [showRows, setShowRows] = useState(true)

  const { data, isLoading, isFetching, refetch } = useIntelligence(statementId ?? undefined, {
    refresh,
    forceOcr,
  })

  const fileUrl = statementId ? statementsApi.previewUrl(statementId) : ''
  const defaultLayoutPluginInstance = defaultLayoutPlugin({ sidebarTabs: () => [] })

  const renderPage = useMemo(
    () => renderPageWithIntelligence(data, { showTables, showColumns, showRows }),
    [data, showTables, showColumns, showRows],
  )

  const handleRefresh = () => {
    setRefresh(true)
    setForceOcr(false)
    void refetch().finally(() => setRefresh(false))
  }

  const handleForceOcr = () => {
    setForceOcr(true)
    setRefresh(true)
    void refetch().finally(() => {
      setRefresh(false)
      setForceOcr(false)
    })
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-2">
          <Brain className="w-7 h-7 text-indigo-400" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">AI Layout Intelligence</h1>
            <p className="text-sm text-zinc-500 mt-1">
              Multi-bank layout detection, OCR fallback, and extraction confidence
            </p>
          </div>
        </div>
      </motion.div>

      {!statementId ? (
        <UploadZone onUploaded={(sid) => navigate(`/intelligence/${sid}`)} />
      ) : (
        <div className="grid lg:grid-cols-[1fr_340px] gap-4">
          <div className="rounded-xl overflow-hidden glass min-h-[520px] relative">
            <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2">
              {(['tables', 'columns', 'rows'] as const).map((key) => {
                const on =
                  key === 'tables' ? showTables : key === 'columns' ? showColumns : showRows
                const toggle = () => {
                  if (key === 'tables') setShowTables(!showTables)
                  if (key === 'columns') setShowColumns(!showColumns)
                  if (key === 'rows') setShowRows(!showRows)
                }
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={toggle}
                    className={cn(
                      'text-xs px-2 py-1 rounded-md capitalize transition-colors',
                      on ? 'bg-indigo-500/30 text-indigo-200' : 'bg-zinc-800/80 text-zinc-500',
                    )}
                  >
                    {key}
                  </button>
                )
              })}
              <button
                type="button"
                onClick={handleRefresh}
                disabled={isFetching}
                className="text-xs px-2 py-1 rounded-md bg-white/5 text-zinc-400 hover:text-zinc-200 flex items-center gap-1"
              >
                <RefreshCw className={cn('w-3 h-3', isFetching && 'animate-spin')} />
                Refresh
              </button>
            </div>
            <Worker workerUrl={WORKER_URL}>
              <Viewer
                fileUrl={fileUrl}
                plugins={[defaultLayoutPluginInstance]}
                renderPage={renderPage}
              />
            </Worker>
          </div>

          <IntelligenceDebugPanel
            data={data}
            loading={isLoading || isFetching}
            onForceOcr={handleForceOcr}
            ocrLoading={isFetching && forceOcr}
          />
        </div>
      )}
    </div>
  )
}
