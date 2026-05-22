import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { UploadZone } from '@/components/pdf/UploadZone'
import { GlassCard } from '@/components/ui/GlassCard'
import { statementsApi } from '@/services/api'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/utils/cn'

export function StatementsPage() {
  const setActiveStatementId = useAppStore((s) => s.setActiveStatementId)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['statements'],
    queryFn: () => statementsApi.list().then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Statements</h1>
        <p className="text-sm text-zinc-500 mt-1">Upload and manage bank statement PDFs</p>
      </div>

      <UploadZone
        compact
        onUploaded={() => refetch()}
      />

      <GlassCard>
        {isLoading && (
          <div className="flex items-center justify-center py-16 text-zinc-500">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            Loading statements…
          </div>
        )}
        {isError && (
          <p className="text-center py-16 text-zinc-500">
            Cannot reach API. Start backend with Docker or uvicorn.
          </p>
        )}
        {data && data.items.length === 0 && (
          <p className="text-center py-16 text-zinc-500">No statements yet. Upload your first PDF.</p>
        )}
        {data && data.items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-zinc-500 border-b border-white/10">
                  <th className="pb-3 font-medium">Filename</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Bank</th>
                  <th className="pb-3 font-medium">Version</th>
                  <th className="pb-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((s, i) => (
                  <motion.tr
                    key={s.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.03 }}
                    className="border-b border-white/5 hover:bg-white/[0.02]"
                  >
                    <td className="py-3 pr-4 font-medium truncate max-w-[200px]">
                      {s.original_filename}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={cn(
                          'px-2 py-0.5 rounded-full text-xs',
                          s.status === 'uploaded' && 'bg-emerald-500/20 text-emerald-400',
                          s.status === 'processing' && 'bg-amber-500/20 text-amber-400',
                          s.status === 'error' && 'bg-red-500/20 text-red-400',
                        )}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-zinc-500">{s.bank_name ?? '—'}</td>
                    <td className="py-3 pr-4 text-zinc-500">
                      v{s.version}
                      {s.page_count != null && (
                        <span className="text-zinc-600"> · {s.page_count}pg</span>
                      )}
                    </td>
                    <td className="py-3 flex gap-3">
                      <Link
                        to={`/preview/${s.id}`}
                        className="text-indigo-400 hover:text-indigo-300"
                        onClick={() => setActiveStatementId(s.id)}
                      >
                        Preview
                      </Link>
                      <Link
                        to={`/transactions/${s.id}`}
                        className="text-emerald-400 hover:text-emerald-300"
                        onClick={() => setActiveStatementId(s.id)}
                      >
                        Transactions
                      </Link>
                      <Link
                        to={`/edit/${s.id}`}
                        className="text-cyan-400 hover:text-cyan-300"
                        onClick={() => setActiveStatementId(s.id)}
                      >
                        Edit
                      </Link>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  )
}
