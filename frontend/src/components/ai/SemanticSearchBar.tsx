import { useState } from 'react'
import { Search } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { aiApi } from '@/services/aiApi'

interface SemanticSearchBarProps {
  statementId: string
  onSelect?: (transactionId: string) => void
}

export function SemanticSearchBar({ statementId, onSelect }: SemanticSearchBarProps) {
  const [q, setQ] = useState('')
  const [submitted, setSubmitted] = useState('')

  const { data, isFetching } = useQuery({
    queryKey: ['ai-search', statementId, submitted],
    queryFn: () => aiApi.semanticSearch(statementId, submitted),
    enabled: submitted.length >= 2,
  })

  return (
    <div className="space-y-2">
      <form
        className="flex gap-1"
        onSubmit={(e) => {
          e.preventDefault()
          setSubmitted(q.trim())
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder='e.g. "travel payments"'
          className="flex-1 rounded-lg bg-zinc-900 border border-white/10 px-2 py-1.5 text-xs text-zinc-200 placeholder:text-zinc-600"
        />
        <button
          type="submit"
          className="p-1.5 rounded-lg bg-indigo-600/80 text-white hover:bg-indigo-500"
          title="Semantic search"
        >
          <Search className="w-4 h-4" />
        </button>
      </form>
      {isFetching && <p className="text-[10px] text-zinc-500">Searching…</p>}
      {data?.results && data.results.length > 0 && (
        <ul className="space-y-1 max-h-32 overflow-y-auto">
          {data.results.map((r) => (
            <li key={r.transaction_id}>
              <button
                type="button"
                onClick={() => onSelect?.(r.transaction_id)}
                className="w-full text-left text-[11px] rounded px-2 py-1 hover:bg-white/5 text-zinc-300"
              >
                <span className="text-indigo-300">{r.category}</span> · {r.description}
                <span className="text-zinc-600 ml-1">({Math.round(r.score * 100)}%)</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
