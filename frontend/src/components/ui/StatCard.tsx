import type { LucideIcon } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { cn } from '@/utils/cn'

interface StatCardProps {
  label: string
  value: string
  icon: LucideIcon
  trend?: string
  delay?: number
  accent?: 'indigo' | 'cyan' | 'purple'
}

const accentMap = {
  indigo: 'from-indigo-500/20 to-indigo-500/5 text-indigo-400',
  cyan: 'from-cyan-500/20 to-cyan-500/5 text-cyan-400',
  purple: 'from-purple-500/20 to-purple-500/5 text-purple-400',
}

export function StatCard({ label, value, icon: Icon, trend, delay = 0, accent = 'indigo' }: StatCardProps) {
  return (
    <GlassCard delay={delay} className="relative overflow-hidden">
      <div
        className={cn(
          'absolute -right-4 -top-4 w-24 h-24 rounded-full bg-gradient-to-br opacity-50 blur-2xl',
          accentMap[accent],
        )}
      />
      <div className="flex items-start justify-between relative">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-2xl font-semibold tracking-tight">{value}</p>
          {trend && <p className="text-xs text-zinc-500 mt-2">{trend}</p>}
        </div>
        <div className={cn('p-2.5 rounded-xl bg-gradient-to-br', accentMap[accent])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </GlassCard>
  )
}
