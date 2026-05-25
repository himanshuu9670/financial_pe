import { motion } from 'framer-motion'
import {
  Brain,
  FileText,
  Table2,
  Home,
  PanelLeftClose,
  PanelLeft,
  Pencil,
  LayoutDashboard,
  FileOutput,
  Settings,
  Shield,
  Sparkles,
  LineChart,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/utils/cn'

const navItems = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/statements', icon: FileText, label: 'Statements' },
  { to: '/transactions', icon: Table2, label: 'Transactions' },
  { to: '/intelligence', icon: Brain, label: 'AI Intelligence' },
  { to: '/insights', icon: LineChart, label: 'AI Insights' },
  { to: '/preview', icon: Sparkles, label: 'Preview' },
  { to: '/workspace', icon: LayoutDashboard, label: 'Workspace' },
  { to: '/edit', icon: Pencil, label: 'Edit Mode' },
  { to: '/export', icon: FileOutput, label: 'Export' },
  { to: '/settings', icon: Settings, label: 'Settings' },
  { to: '/admin', icon: Shield, label: 'Admin' },
]

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore()

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 72 : 256 }}
      className={cn(
        'fixed left-0 top-0 z-40 h-screen glass border-r border-white/10 flex flex-col',
      )}
    >
      <div className="flex items-center gap-3 px-4 h-16 border-b border-white/10">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shrink-0">
          <FileText className="w-5 h-5 text-white" />
        </div>
        {!sidebarCollapsed && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="overflow-hidden">
            <p className="font-semibold text-sm tracking-tight">StatementForge</p>
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest">PDF Editor</p>
          </motion.div>
        )}
      </div>

      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-indigo-500/20 text-indigo-300 neon-border'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/5',
              )
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!sidebarCollapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <button
        type="button"
        onClick={toggleSidebar}
        className="m-3 p-2 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-colors"
        aria-label="Toggle sidebar"
      >
        {sidebarCollapsed ? (
          <PanelLeft className="w-5 h-5" />
        ) : (
          <PanelLeftClose className="w-5 h-5" />
        )}
      </button>
    </motion.aside>
  )
}
