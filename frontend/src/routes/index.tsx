import { lazy, Suspense, type ComponentType, type ReactNode } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'

import { DashboardLayout } from '@/layouts/DashboardLayout'
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout'
import { HomePage } from '@/pages/HomePage'

const PreviewPage = lazy(() => import('@/pages/PreviewPage').then((m) => ({ default: m.PreviewPage })))
const StatementsPage = lazy(() =>
  import('@/pages/StatementsPage').then((m) => ({ default: m.StatementsPage })),
)
const TransactionsPage = lazy(() =>
  import('@/pages/TransactionsPage').then((m) => ({ default: m.TransactionsPage })),
)
const IntelligencePage = lazy(() =>
  import('@/pages/IntelligencePage').then((m) => ({ default: m.IntelligencePage })),
)
const InsightsPage = lazy(() => import('@/pages/InsightsPage').then((m) => ({ default: m.InsightsPage })))
const WorkspacePage = lazy(() => import('@/pages/WorkspacePage').then((m) => ({ default: m.WorkspacePage })))
const ComparePage = lazy(() => import('@/pages/ComparePage').then((m) => ({ default: m.ComparePage })))
const HistoryPage = lazy(() => import('@/pages/HistoryPage').then((m) => ({ default: m.HistoryPage })))
const ValidationPage = lazy(() =>
  import('@/pages/ValidationPage').then((m) => ({ default: m.ValidationPage })),
)
const EditModePage = lazy(() => import('@/pages/EditModePage').then((m) => ({ default: m.EditModePage })))
const ExportPage = lazy(() => import('@/pages/ExportPage').then((m) => ({ default: m.ExportPage })))
const SettingsPage = lazy(() => import('@/pages/SettingsPage').then((m) => ({ default: m.SettingsPage })))
const LoginPage = lazy(() => import('@/pages/LoginPage').then((m) => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('@/pages/RegisterPage').then((m) => ({ default: m.RegisterPage })))
const AdminPage = lazy(() => import('@/pages/AdminPage').then((m) => ({ default: m.AdminPage })))

function Lazy({ children }: { children: ReactNode }) {
  return <Suspense fallback={<div className="p-8 text-zinc-500 animate-pulse">Loading…</div>}>{children}</Suspense>
}

const workspaceRoute = (Page: ComponentType) => ({
  element: <WorkspaceLayout />,
  children: [
    {
      index: true,
      element: (
        <Lazy>
          <Page />
        </Lazy>
      ),
    },
  ],
})

export const router = createBrowserRouter([
  { path: '/workspace/:id?', ...workspaceRoute(WorkspacePage) },
  { path: '/compare/:id?', ...workspaceRoute(ComparePage) },
  { path: '/history/:id?', ...workspaceRoute(HistoryPage) },
  { path: '/validation/:id?', ...workspaceRoute(ValidationPage) },
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'statements', element: <Lazy><StatementsPage /></Lazy> },
      { path: 'transactions/:id?', element: <Lazy><TransactionsPage /></Lazy> },
      { path: 'intelligence/:id?', element: <Lazy><IntelligencePage /></Lazy> },
      { path: 'insights/:id?', element: <Lazy><InsightsPage /></Lazy> },
      { path: 'preview/:id?', element: <Lazy><PreviewPage /></Lazy> },
      { path: 'edit/:id?', element: <Lazy><EditModePage /></Lazy> },
      { path: 'export/:id?', element: <Lazy><ExportPage /></Lazy> },
      { path: 'settings', element: <Lazy><SettingsPage /></Lazy> },
      { path: 'login', element: <Lazy><LoginPage /></Lazy> },
      { path: 'register', element: <Lazy><RegisterPage /></Lazy> },
      { path: 'admin', element: <Lazy><AdminPage /></Lazy> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
