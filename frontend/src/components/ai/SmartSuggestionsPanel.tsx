import { Sparkles, Wand2 } from 'lucide-react'
import type { SmartCorrection, SmartSuggestion } from '@/types/ai'
import { cn } from '@/utils/cn'

interface SmartSuggestionsPanelProps {
  suggestions: SmartSuggestion[]
  corrections: SmartCorrection[]
}

export function SmartSuggestionsPanel({
  suggestions,
  corrections,
}: SmartSuggestionsPanelProps) {
  return (
    <div className="space-y-3">
      {corrections.length > 0 && (
        <section>
          <h4 className="text-[10px] uppercase tracking-wider text-zinc-500 flex items-center gap-1 mb-2">
            <Wand2 className="w-3 h-3" /> OCR corrections
          </h4>
          <ul className="space-y-1.5">
            {corrections.slice(0, 5).map((c, i) => (
              <li
                key={`${c.field}-${i}`}
                className="text-[11px] rounded-md bg-zinc-900/80 border border-cyan-500/20 px-2 py-1.5"
              >
                <span className="text-zinc-400">{c.field}:</span>{' '}
                <span className="line-through text-zinc-500">{c.original}</span>{' '}
                <span className="text-cyan-300">→ {c.corrected}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h4 className="text-[10px] uppercase tracking-wider text-zinc-500 flex items-center gap-1 mb-2">
          <Sparkles className="w-3 h-3" /> Smart suggestions
        </h4>
        <ul className="space-y-1.5 max-h-48 overflow-y-auto">
          {suggestions.slice(0, 12).map((s) => (
            <li
              key={s.id}
              className={cn(
                'text-[11px] rounded-md border px-2 py-1.5',
                s.severity === 'high'
                  ? 'border-rose-500/30 bg-rose-950/30'
                  : 'border-white/10 bg-zinc-900/60',
              )}
            >
              <p className="font-medium text-zinc-200">{s.title}</p>
              <p className="text-zinc-500">{s.message}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
