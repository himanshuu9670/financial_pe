import { motion } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'
import type { ChangeType } from '@/types/editSession'
import { pdfBboxToViewport } from '@/utils/coordinates'
import { cn } from '@/utils/cn'

interface OverlayEditorProps {
  bbox: [number, number, number, number]
  scale: number
  initialValue: string
  field: ChangeType
  onCommit: (value: string | null) => void
  onCancel: () => void
}

export function OverlayEditor({
  bbox,
  scale,
  initialValue,
  field,
  onCommit,
  onCancel,
}: OverlayEditorProps) {
  const rect = pdfBboxToViewport(bbox, scale)
  const [draft, setDraft] = useState(initialValue.replace(/,/g, ''))
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
    inputRef.current?.select()
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="absolute z-50 pointer-events-auto"
      style={{
        left: rect.left - 2,
        top: rect.top - 2,
        minWidth: Math.max(rect.width + 16, 72),
      }}
    >
      <input
        ref={inputRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            onCommit(draft.trim() === '' ? null : draft.replace(/,/g, ''))
          }
          if (e.key === 'Escape') onCancel()
        }}
        onBlur={() => onCommit(draft.trim() === '' ? null : draft.replace(/,/g, ''))}
        className={cn(
          'w-full px-2 py-1 rounded-md text-sm font-mono',
          'bg-zinc-900/95 border-2 border-cyan-400 shadow-[0_0_24px_rgba(34,211,238,0.45)]',
          'text-cyan-50 outline-none',
        )}
        aria-label={`Edit ${field}`}
      />
    </motion.div>
  )
}
