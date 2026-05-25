import type { LedgerEntry } from '@/types/editSession'
import { fmtAmount } from '@/utils/workspace'

interface TransactionDetailsPanelProps {
  entry: LedgerEntry | undefined
}

export function TransactionDetailsPanel({ entry }: TransactionDetailsPanelProps) {
  if (!entry) {
    return (
      <p className="p-4 text-sm text-zinc-600">
        Select a transaction in the PDF or table to inspect details.
      </p>
    )
  }

  return (
    <div className="p-4 space-y-3 text-sm">
      <div>
        <p className="text-zinc-500 text-xs">Description</p>
        <p className="text-zinc-100">{entry.description || '—'}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <p className="text-zinc-500 text-xs">Debit</p>
          <p className="font-mono text-rose-300">{fmtAmount(entry.debit) || '—'}</p>
        </div>
        <div>
          <p className="text-zinc-500 text-xs">Credit</p>
          <p className="font-mono text-emerald-300">{fmtAmount(entry.credit) || '—'}</p>
        </div>
        <div className="col-span-2">
          <p className="text-zinc-500 text-xs">Balance</p>
          <p className="font-mono text-cyan-300">{fmtAmount(entry.balance) || '—'}</p>
        </div>
      </div>
      {entry.validation_warnings.length > 0 && (
        <ul className="text-xs text-amber-400/90 space-y-1">
          {entry.validation_warnings.map((w, i) => (
            <li key={i}>• {w}</li>
          ))}
        </ul>
      )}
      <p className="text-[10px] text-zinc-600 font-mono">
        Page {entry.page} · Row {entry.row_index}
      </p>
    </div>
  )
}
