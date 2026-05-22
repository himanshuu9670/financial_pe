import { useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { FileUp, Loader2, Upload } from 'lucide-react'
import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { usePdfStore } from '@/store/usePdfStore'
import { cn } from '@/utils/cn'

interface UploadZoneProps {
  onUploaded?: (statementId: string) => void
  compact?: boolean
}

export function UploadZone({ onUploaded, compact = false }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setActiveStatementId = useAppStore((s) => s.setActiveStatementId)
  const setStatement = usePdfStore((s) => s.setStatement)

  const uploadMutation = useMutation({
    mutationFn: (file: File) => statementsApi.upload(file).then((r) => r.data),
    onSuccess: (data) => {
      setActiveStatementId(data.statement_id)
      setStatement(
        data.statement_id,
        data.filename,
        statementsApi.previewUrl(data.statement_id),
        data.page_count ?? 0,
      )
      queryClient.invalidateQueries({ queryKey: ['statements'] })
      onUploaded?.(data.statement_id)
      if (!onUploaded) navigate(`/preview/${data.statement_id}`)
    },
  })

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0]
      if (!file) return
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        uploadMutation.reset()
        return
      }
      uploadMutation.mutate(file)
    },
    [uploadMutation],
  )

  return (
    <motion.div
      layout
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        handleFiles(e.dataTransfer.files)
      }}
      onClick={() => !uploadMutation.isPending && inputRef.current?.click()}
      className={cn(
        'glass rounded-2xl border-2 border-dashed transition-all cursor-pointer',
        compact ? 'p-8' : 'p-12',
        dragOver
          ? 'border-cyan-400/60 bg-cyan-500/10'
          : 'border-white/15 hover:border-indigo-400/40 hover:bg-white/[0.03]',
        uploadMutation.isPending && 'pointer-events-none opacity-70',
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      <div className="flex flex-col items-center text-center gap-4">
        <div
          className={cn(
            'rounded-2xl p-4 bg-gradient-to-br from-indigo-500/20 to-cyan-500/10',
            dragOver && 'scale-110 transition-transform',
          )}
        >
          {uploadMutation.isPending ? (
            <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
          ) : dragOver ? (
            <FileUp className="w-10 h-10 text-cyan-400" />
          ) : (
            <Upload className="w-10 h-10 text-indigo-400" />
          )}
        </div>
        <div>
          <p className="font-semibold text-lg">
            {uploadMutation.isPending ? 'Uploading…' : 'Drop bank statement PDF'}
          </p>
          <p className="text-sm text-zinc-500 mt-1">or click to browse · max 50MB · PDF only</p>
        </div>
        {!compact && (
          <p className="text-xs text-zinc-600">YES Bank · Axis Bank · Canara Bank layouts supported</p>
        )}
      </div>

      {uploadMutation.isError && (
        <p className="text-sm text-red-400 text-center mt-4">
          Upload failed. Check backend connection and file format.
        </p>
      )}
    </motion.div>
  )
}
