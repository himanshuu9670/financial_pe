import { createBrowserRouter, Navigate } from 'react-router-dom'
import { DashboardLayout } from '@/layouts/DashboardLayout'
import { EditModePage } from '@/pages/EditModePage'
import { HomePage } from '@/pages/HomePage'
import { PreviewPage } from '@/pages/PreviewPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { StatementsPage } from '@/pages/StatementsPage'
import { TransactionsPage } from '@/pages/TransactionsPage'
import { ExportPage } from '@/pages/ExportPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'statements', element: <StatementsPage /> },
      { path: 'transactions/:id?', element: <TransactionsPage /> },
      { path: 'preview/:id?', element: <PreviewPage /> },
      { path: 'edit/:id?', element: <EditModePage /> },
      { path: 'export/:id?', element: <ExportPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
