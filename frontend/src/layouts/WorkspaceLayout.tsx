import { Outlet } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { ArrowLeft, FileText } from 'lucide-react'

/** Full-bleed layout for Phase 7 editing workspace (no content max-width). */
export function WorkspaceLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#0a0a0f]">
      <header className="h-12 shrink-0 flex items-center gap-4 px-4 border-b border-white/10 bg-zinc-950/90 backdrop-blur-md">
        <Link
          to="/"
          className="flex items-center gap-2 text-zinc-500 hover:text-zinc-200 text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Home
        </Link>
        <div className="flex items-center gap-2 text-zinc-300">
          <FileText className="w-4 h-4 text-indigo-400" />
          <span className="text-sm font-medium">StatementForge Workspace</span>
        </div>
        <nav className="ml-auto flex gap-4 text-xs text-zinc-500">
          <Link to="/workspace" className="hover:text-cyan-300">
            Workspace
          </Link>
          <Link to="/compare" className="hover:text-cyan-300">
            Compare
          </Link>
          <Link to="/history" className="hover:text-cyan-300">
            History
          </Link>
          <Link to="/validation" className="hover:text-cyan-300">
            Validation
          </Link>
        </nav>
      </header>
      <Outlet />
    </div>
  )
}
