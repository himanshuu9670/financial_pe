import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { CategorySpend } from '@/types/ai'

interface SpendingTrendChartProps {
  data: CategorySpend[]
}

/** Debit totals by category — trend-style area chart for dashboard. */
export function SpendingTrendChart({ data }: SpendingTrendChartProps) {
  const chartData = [...data]
    .filter((d) => d.total_debit > 0)
    .sort((a, b) => b.total_debit - a.total_debit)
    .slice(0, 8)
    .map((d) => ({ name: d.category, debit: d.total_debit, count: d.count }))

  if (!chartData.length) {
    return <p className="text-xs text-zinc-500 px-2">No spending data for trend chart.</p>
  }

  return (
    <div className="h-40 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="debitGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#a1a1aa' }} />
          <YAxis tick={{ fontSize: 9, fill: '#a1a1aa' }} />
          <Tooltip
            contentStyle={{
              background: '#18181b',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              fontSize: 11,
            }}
          />
          <Area
            type="monotone"
            dataKey="debit"
            stroke="#818cf8"
            fill="url(#debitGrad)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
