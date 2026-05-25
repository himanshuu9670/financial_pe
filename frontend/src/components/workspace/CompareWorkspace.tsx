import { Worker, Viewer } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { Columns2, Link2 } from 'lucide-react'
import { useState } from 'react'
import { exportApi } from '@/services/exportApi'
import { statementsApi } from '@/services/api'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { cn } from '@/utils/cn'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

interface CompareWorkspaceProps {
  statementId: string
}

export function CompareWorkspace({ statementId }: CompareWorkspaceProps) {
  const syncScroll = useWorkspaceStore((s) => s.syncScroll)
  const setSyncScroll = useWorkspaceStore((s) => s.setSyncScroll)
  const [editedUrl, setEditedUrl] = useState<string | null>(null)
  const originalUrl = statementsApi.previewUrl(statementId)

  const plugin = defaultLayoutPlugin({ sidebarTabs: () => [] })

  const loadEdited = async () => {
    try {
      await exportApi.applyEdits({ statement_id: statementId })
      setEditedUrl(exportApi.previewEdited(statementId))
    } catch {
      setEditedUrl(null)
    }
  }

  return (
    <div className="p-4 space-y-4 h-[calc(100vh-3rem)] flex flex-col">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-semibold">Compare mode</h1>
        <button
          type="button"
          onClick={() => setSyncScroll(!syncScroll)}
          className={cn(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs border',
            syncScroll
              ? 'border-cyan-500/40 bg-cyan-500/15 text-cyan-300'
              : 'border-white/10 text-zinc-500',
          )}
        >
          <Link2 className="w-4 h-4" />
          Sync scroll {syncScroll ? 'on' : 'off'}
        </button>
        <button
          type="button"
          onClick={loadEdited}
          className="px-3 py-1.5 rounded-lg text-xs bg-indigo-600 hover:bg-indigo-500"
        >
          Generate edited preview
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-4 flex-1 min-h-0">
        <div className="glass rounded-xl overflow-hidden flex flex-col min-h-[400px]">
          <p className="text-xs text-zinc-500 px-3 py-2 border-b border-white/10 flex items-center gap-2">
            <Columns2 className="w-4 h-4" />
            Original
          </p>
          <div className="flex-1 overflow-auto">
            <Worker workerUrl={WORKER_URL}>
              <Viewer fileUrl={originalUrl} plugins={[plugin]} />
            </Worker>
          </div>
        </div>
        <div className="glass rounded-xl overflow-hidden flex flex-col min-h-[400px]">
          <p className="text-xs text-zinc-500 px-3 py-2 border-b border-white/10">Edited</p>
          <div className="flex-1 overflow-auto">
            {editedUrl ? (
              <Worker workerUrl={WORKER_URL}>
                <Viewer fileUrl={editedUrl} plugins={[plugin]} />
              </Worker>
            ) : (
              <p className="p-8 text-sm text-zinc-600 text-center">
                Commit edits in workspace, then generate edited preview.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
