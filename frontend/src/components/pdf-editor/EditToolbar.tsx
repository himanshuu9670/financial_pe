import {
  Bug,
  Columns2,
  Maximize2,
  Minus,
  Plus,
  Redo2,
  ScanLine,
  ShieldCheck,
  Sparkles,
  Undo2,
  ZoomIn,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useWorkspaceStore } from '@/store/useWorkspaceStore'
import { cn } from '@/utils/cn'

interface EditToolbarProps {
  statementId: string
  canUndo: boolean
  canRedo: boolean
  onUndo: () => void
  onRedo: () => void
  isUpdating?: boolean
}

export function EditToolbar({
  statementId,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  isUpdating,
}: EditToolbarProps) {
  const pdfScale = useWorkspaceStore((s) => s.pdfScale)
  const setPdfScale = useWorkspaceStore((s) => s.setPdfScale)
  const showDebug = useWorkspaceStore((s) => s.showDebugTools)
  const setShowDebug = useWorkspaceStore((s) => s.setShowDebugTools)
  const showLive = useWorkspaceStore((s) => s.showLivePreview)
  const setShowLive = useWorkspaceStore((s) => s.setShowLivePreview)
  const showValidation = useWorkspaceStore((s) => s.showValidationOverlay)
  const setShowValidation = useWorkspaceStore((s) => s.setShowValidationOverlay)
  const showOcr = useWorkspaceStore((s) => s.showOcrHints)
  const setShowOcr = useWorkspaceStore((s) => s.setShowOcrHints)

  const btn =
    'p-2 rounded-lg border border-white/10 hover:bg-white/5 text-zinc-400 hover:text-zinc-100 transition-colors disabled:opacity-40'

  return (
    <div className="flex flex-wrap items-center gap-1 px-3 py-2 border-b border-white/10 bg-zinc-950/80 backdrop-blur-md">
      <button type="button" className={btn} onClick={onUndo} disabled={!canUndo || isUpdating} title="Undo (Ctrl+Z)">
        <Undo2 className="w-4 h-4" />
      </button>
      <button type="button" className={btn} onClick={onRedo} disabled={!canRedo || isUpdating} title="Redo (Ctrl+Y)">
        <Redo2 className="w-4 h-4" />
      </button>

      <span className="w-px h-6 bg-white/10 mx-1" />

      <button type="button" className={btn} onClick={() => setPdfScale(pdfScale - 0.1)} title="Zoom out">
        <Minus className="w-4 h-4" />
      </button>
      <span className="text-xs text-zinc-500 font-mono w-12 text-center">
        {Math.round(pdfScale * 100)}%
      </span>
      <button type="button" className={btn} onClick={() => setPdfScale(pdfScale + 0.1)} title="Zoom in">
        <Plus className="w-4 h-4" />
      </button>
      <button type="button" className={btn} onClick={() => setPdfScale(1)} title="Fit 100%">
        <Maximize2 className="w-4 h-4" />
      </button>

      <span className="w-px h-6 bg-white/10 mx-1" />

      <button
        type="button"
        className={cn(btn, showLive && 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30')}
        onClick={() => setShowLive(!showLive)}
        title="Live preview values"
      >
        <Sparkles className="w-4 h-4" />
      </button>
      <button
        type="button"
        className={cn(btn, showValidation && 'bg-emerald-500/20 text-emerald-300')}
        onClick={() => setShowValidation(!showValidation)}
        title="Validation overlay"
      >
        <ShieldCheck className="w-4 h-4" />
      </button>
      <button
        type="button"
        className={cn(btn, showOcr && 'bg-orange-500/20 text-orange-300')}
        onClick={() => setShowOcr(!showOcr)}
        title="OCR hints"
      >
        <ScanLine className="w-4 h-4" />
      </button>
      <button
        type="button"
        className={cn(btn, showDebug && 'bg-pink-500/20 text-pink-300')}
        onClick={() => setShowDebug(!showDebug)}
        title="Debug coordinates"
      >
        <Bug className="w-4 h-4" />
      </button>

      <span className="flex-1" />

      <Link
        to={`/compare/${statementId}`}
        className={cn(btn, 'inline-flex items-center gap-1.5 text-xs px-3')}
      >
        <Columns2 className="w-4 h-4" />
        Compare
      </Link>
      <Link
        to={`/export/${statementId}`}
        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs bg-indigo-600 hover:bg-indigo-500 text-white"
      >
        <ZoomIn className="w-4 h-4" />
        Export
      </Link>

      {isUpdating && (
        <span className="text-xs text-cyan-400 animate-pulse ml-2">Syncing…</span>
      )}
    </div>
  )
}
