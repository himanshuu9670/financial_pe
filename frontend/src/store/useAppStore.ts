import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  sidebarCollapsed: boolean
  activeStatementId: string | null
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  setActiveStatementId: (id: string | null) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      activeStatementId: null,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setActiveStatementId: (id) => set({ activeStatementId: id }),
    }),
    { name: 'pdf-editor-app' },
  ),
)
