import { useEffect } from 'react'

interface ShortcutHandlers {
  onUndo?: () => void
  onRedo?: () => void
  onEscape?: () => void
  onZoomIn?: () => void
  onZoomOut?: () => void
  onFit?: () => void
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers, enabled = true) {
  useEffect(() => {
    if (!enabled) return

    const onKey = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        handlers.onUndo?.()
      }
      if (mod && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault()
        handlers.onRedo?.()
      }
      if (e.key === 'Escape') handlers.onEscape?.()
      if (mod && (e.key === '=' || e.key === '+')) {
        e.preventDefault()
        handlers.onZoomIn?.()
      }
      if (mod && e.key === '-') {
        e.preventDefault()
        handlers.onZoomOut?.()
      }
      if (mod && e.key === '0') {
        e.preventDefault()
        handlers.onFit?.()
      }
    }

    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [handlers, enabled])
}
