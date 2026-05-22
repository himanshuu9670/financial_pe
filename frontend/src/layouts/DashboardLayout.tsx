import { motion } from 'framer-motion'
import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/navigation/Sidebar'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/utils/cn'

export function DashboardLayout() {
  const collapsed = useAppStore((s) => s.sidebarCollapsed)

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <motion.main
        layout
        className={cn(
          'flex-1 flex flex-col min-h-screen transition-all duration-300',
          collapsed ? 'ml-[72px]' : 'ml-64',
        )}
      >
        <div className="flex-1 p-6 md:p-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </div>
      </motion.main>
    </div>
  )
}
