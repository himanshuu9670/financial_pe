import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import { pageNavigationPlugin } from '@react-pdf-viewer/page-navigation'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import { useQueryClient } from '@tanstack/react-query'
import {
  Bug,
  Building2,
  Loader2,
  RefreshCw,
  Rows3,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import { GlassCard } from '@/components/ui/GlassCard'
import { renderPageWithLayers } from '@/components/pdf/TransactionOverlay'
import { TransactionTable } from '@/components/transactions/TransactionTable'
import { usePdfExtraction } from '@/hooks/usePdfExtraction'
import { useTransactions } from '@/hooks/useTransactions'
import { statementsApi } from '@/services/api'
import { usePdfStore } from '@/store/usePdfStore'
import { useTransactionStore } from '@/store/useTransactionStore'
import type { PageExtraction } from '@/types/extraction'
import type { ParsedTransaction } from '@/types/transaction'
import { cn } from '@/utils/cn'

const WORKER_URL = 'https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'

interface TransactionExplorerProps {
  statementId: string
}

export function TransactionExplorer({ statementId }: TransactionExplorerProps) {
  const queryClient = useQueryClient()
  const jumpToPageRef = useRef<(pageIndex: number) => void>(() => {})

  const fileUrl = usePdfStore((s) => s.fileUrl) ?? statementsApi.previewUrl(statementId)
  const extraction = usePdfStore((s) => s.extraction)
  const debugMode = useTransactionStore((s) => s.debugMode)
  const setShowColumnGuides = useTransactionStore((s) => s.setShowColumnGuides)
  const showSpanOverlay = useTransactionStore((s) => s.showSpanOverlay)
  const txnData = useTransactionStore((s) => s.data)
  const txnLoading = useTransactionStore((s) => s.loading)
  const txnError = useTransactionStore((s) => s.error)

  const { isFetching: extracting } = usePdfExtraction(statementId)
  const { refetch: refetchTxns, isFetching: reparsing } = useTransactions(
    statementId,
    debugMode,
  )

  const pageNavigationPluginInstance = pageNavigationPlugin()
  jumpToPageRef.current = pageNavigationPluginInstance.jumpToPage

  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: () => [],
  })

  const pageDataByIndex = useMemo(() => {
    const map = new Map<number, PageExtraction>()
    extraction?.pages.forEach((p) => map.set(p.page, p))
    return map
  }, [extraction])

  const transactions = txnData?.transactions ?? []

  const renderPage = useMemo(
    () => renderPageWithLayers(pageDataByIndex, transactions, showSpanOverlay),
    [pageDataByIndex, transactions, showSpanOverlay],
  )

  useEffect(() => {
    setShowColumnGuides(debugMode)
  }, [debugMode, setShowColumnGuides])

  const handleTableSelect = useCallback((txn: ParsedTransaction) => {
    jumpToPageRef.current(txn.page - 1)
    usePdfStore.getState().setCurrentPage(txn.page)
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        {txnData && (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg glass text-sm">
            <Building2 className="w-4 h-4 text-indigo-400" />
            <span className="text-zinc-300">{txnData.bank.replace(/_/g, ' ')}</span>
            <span className="text-zinc-600 text-xs">
              {(txnData.bank_confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
        )}

        <button
          type="button"
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['transactions', statementId] })
            refetchTxns()
          }}
          disabled={reparsing}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border border-white/10 text-zinc-400 hover:text-zinc-200"
        >
          <RefreshCw className={cn('w-4 h-4', reparsing && 'animate-spin')} />
          Re-parse
        </button>

        <label className="inline-flex items-center gap-2 text-sm text-zinc-500 cursor-pointer">
          <input
            type="checkbox"
            checked={debugMode}
            onChange={(e) => useTransactionStore.getState().setDebugMode(e.target.checked)}
            className="rounded border-white/20"
          />
          <Bug className="w-4 h-4" />
          Debug
        </label>

        <label className="inline-flex items-center gap-2 text-sm text-zinc-500 cursor-pointer">
          <input
            type="checkbox"
            checked={useTransactionStore.getState().showRowBboxes}
            onChange={(e) => useTransactionStore.getState().setShowRowBboxes(e.target.checked)}
            className="rounded border-white/20"
          />
          <Rows3 className="w-4 h-4" />
          Row boxes
        </label>

        {(txnLoading || extracting || reparsing) && (
          <span className="inline-flex items-center gap-1 text-xs text-indigo-400">
            <Loader2 className="w-3 h-3 animate-spin" />
            Processing…
          </span>
        )}
      </div>

      {txnData?.warnings.map((w) => (
        <p key={w} className="text-xs text-amber-500/90">
          {w}
        </p>
      ))}

      {txnError && <p className="text-sm text-red-400">{txnError}</p>}

      {!txnData?.summary.validation_passed && txnData?.summary.validation_issues.length ? (
        <div className="text-xs text-amber-400 glass rounded-lg px-4 py-2 border border-amber-500/20">
          Balance validation: {txnData.summary.validation_issues.length} issue(s) — review flagged rows.
        </div>
      ) : null}

      <div className="grid xl:grid-cols-5 gap-4 min-h-[640px]">
        <GlassCard className="xl:col-span-3 p-0 overflow-hidden [&_.rpv-core__viewer]:min-h-[600px]">
          <Worker workerUrl={WORKER_URL}>
            <Viewer
              fileUrl={fileUrl}
              plugins={[pageNavigationPluginInstance, defaultLayoutPluginInstance]}
              renderPage={renderPage}
            />
          </Worker>
        </GlassCard>

        <GlassCard className="xl:col-span-2 p-0 flex flex-col min-h-[600px] overflow-hidden">
          <div className="p-3 border-b border-white/10">
            <h2 className="font-semibold text-sm">
              Transactions
              {txnData && (
                <span className="text-zinc-500 font-normal ml-2">
                  ({txnData.transactions.length})
                </span>
              )}
            </h2>
          </div>
          <TransactionTable onSelect={handleTableSelect} />
        </GlassCard>
      </div>

      {debugMode && txnData?.debug && (
        <GlassCard className="text-xs font-mono text-zinc-500 space-y-2">
          <p>Grouped rows: {txnData.debug.grouped_row_count}</p>
          <p>Columns: {txnData.debug.columns.map((c) => c.name).join(', ')}</p>
          <p>Header row index: {txnData.debug.header_row_index ?? 'n/a'}</p>
        </GlassCard>
      )}
    </div>
  )
}
