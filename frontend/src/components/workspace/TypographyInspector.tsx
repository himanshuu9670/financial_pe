import type { LedgerEntry } from '@/types/editSession'

interface TypographyInspectorProps {
  entry: LedgerEntry | undefined
}

export function TypographyInspector({ entry }: TypographyInspectorProps) {
  if (!entry) {
    return <p className="p-4 text-sm text-zinc-600">No transaction selected.</p>
  }

  const meta = entry.font_metadata ?? {}
  const coords = entry.coordinates

  return (
    <div className="p-4 space-y-3 text-xs font-mono text-zinc-400">
      <p className="text-zinc-500 text-[10px] uppercase tracking-wider">Font metadata</p>
      <pre className="rounded-lg bg-black/40 p-2 overflow-auto max-h-32 text-[10px]">
        {JSON.stringify(meta, null, 2)}
      </pre>
      {coords && (
        <>
          <p className="text-zinc-500 text-[10px] uppercase tracking-wider">Field positions</p>
          <ul className="space-y-1">
            {(['debit', 'credit', 'balance', 'description'] as const).map((f) => {
              const c = coords[f]
              if (!c) return null
              return (
                <li key={f}>
                  <span className="text-cyan-400">{f}</span>: {c.font} {c.font_size}pt @ ({c.x},{c.y})
                </li>
              )
            })}
          </ul>
        </>
      )}
    </div>
  )
}
