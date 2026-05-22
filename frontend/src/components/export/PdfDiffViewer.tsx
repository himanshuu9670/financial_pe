import { Worker, Viewer } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { motion } from 'framer-motion'
import { Columns2, Rows2 } from 'lucide-react'
import { useState } from 'react'
import { GlassCard } from '@/components/ui/GlassCard'
import { cn } from '@/utils/cn'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

interface PdfDiffViewerProps {
  originalUrl: string
  editedUrl: string
}

export function PdfDiffViewer({ originalUrl, editedUrl }: PdfDiffViewerProps) {
  const [layout, setLayout] = useState<'side' | 'stack'>('side')
  const plugin = defaultLayoutPlugin({ sidebarTabs: () => [] })

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setLayout('side')}
          className={cn(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border',
            layout === 'side'
              ? 'border-indigo-500/50 bg-indigo-500/20 text-indigo-300'
              : 'border-white/10 text-zinc-500',
          )}
        >
          <Columns2 className="w-4 h-4" />
          Side by side
        </button>
        <button
          type="button"
          onClick={() => setLayout('stack')}
          className={cn(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border',
            layout === 'stack'
              ? 'border-indigo-500/50 bg-indigo-500/20 text-indigo-300'
              : 'border-white/10 text-zinc-500',
          )}
        >
          <Rows2 className="w-4 h-4" />
          Stacked
        </button>
      </div>

      <motion.div
        layout
        className={cn(
          'grid gap-4',
          layout === 'side' ? 'lg:grid-cols-2' : 'grid-cols-1',
        )}
      >
        <GlassCard className="p-0 overflow-hidden">
          <p className="text-xs text-zinc-500 px-3 py-2 border-b border-white/10">Original</p>
          <div className="min-h-[420px] [&_.rpv-core__viewer]:min-h-[400px]">
            <Worker workerUrl={WORKER_URL}>
              <Viewer fileUrl={originalUrl} plugins={[plugin]} />
            </Worker>
          </div>
        </GlassCard>
        <GlassCard className="p-0 overflow-hidden neon-border">
          <p className="text-xs text-cyan-400/90 px-3 py-2 border-b border-white/10">Edited export</p>
          <div className="min-h-[420px] [&_.rpv-core__viewer]:min-h-[400px]">
            <Worker workerUrl={WORKER_URL}>
              <Viewer fileUrl={editedUrl} plugins={[plugin]} />
            </Worker>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  )
}
