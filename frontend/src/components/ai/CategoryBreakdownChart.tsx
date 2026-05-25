import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'
import type { CategorySpend } from '@/types/ai'

const COLORS = [
  '#22d3ee',
  '#818cf8',
  '#a78bfa',
  '#f472b6',
  '#fb923c',
  '#4ade80',
  '#facc15',
  '#94a3b8',
]

interface CategoryBreakdownChartProps {
  data: CategorySpend[]
}

export function CategoryBreakdownChart({ data }: CategoryBreakdownChartProps) {
  const chartData = data
    .filter((d) => d.total_debit > 0)
    .map((d) => ({ name: d.category, value: d.total_debit }))

  if (!chartData.length) {
    return <p className="text-xs text-zinc-500 p-4">No debit spending to chart yet.</p>
  }

  return (
    <div className="h-52 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={45}
            outerRadius={70}
            paddingAngle={2}
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: '#18181b',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              fontSize: 11,
            }}
            formatter={(v: number) => [`₹${v.toLocaleString()}`, 'Debit']}
          />
          <Legend wrapperStyle={{ fontSize: 10 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
