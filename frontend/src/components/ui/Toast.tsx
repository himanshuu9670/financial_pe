import { AnimatePresence, motion } from 'framer-motion'
import { create } from 'zustand'
import { X } from 'lucide-react'
import { cn } from '@/utils/cn'

type ToastType = 'info' | 'success' | 'error'

interface ToastItem {
  id: string
  message: string
  type: ToastType
}

interface ToastState {
  items: ToastItem[]
  push: (message: string, type?: ToastType) => void
  dismiss: (id: string) => void
}

export const useToastStore = create<ToastState>((set) => ({
  items: [],
  push: (message, type = 'info') => {
    const id = crypto.randomUUID()
    set((s) => ({ items: [...s.items, { id, message, type }] }))
    setTimeout(() => {
      set((s) => ({ items: s.items.filter((t) => t.id !== id) }))
    }, 5000)
  },
  dismiss: (id) => set((s) => ({ items: s.items.filter((t) => t.id !== id) })),
}))

export function toast(message: string, type: ToastType = 'info') {
  useToastStore.getState().push(message, type)
}

export function ToastContainer() {
  const items = useToastStore((s) => s.items)
  const dismiss = useToastStore((s) => s.dismiss)

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
      <AnimatePresence>
        {items.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 40 }}
            className={cn(
              'flex items-start gap-2 px-4 py-3 rounded-lg border shadow-lg backdrop-blur-md text-sm',
              t.type === 'success' && 'bg-emerald-500/20 border-emerald-500/40 text-emerald-100',
              t.type === 'error' && 'bg-red-500/20 border-red-500/40 text-red-100',
              t.type === 'info' && 'bg-zinc-900/90 border-white/10 text-zinc-200',
            )}
          >
            <span className="flex-1">{t.message}</span>
            <button type="button" onClick={() => dismiss(t.id)} className="opacity-60 hover:opacity-100">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
