import { useEffect, useRef } from 'react'

const WS_BASE =
  (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(
    /^http/,
    'ws',
  )

/**
 * WebSocket foundation — subscribe channel for future multi-user sync.
 * Currently pings only; state still driven by REST mutations.
 */
export function useEditWebSocket(sessionId: string | null, enabled = true) {
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!sessionId || !enabled) return

    const url = `${WS_BASE}/ws/edit/${sessionId}`
    let ws: WebSocket
    try {
      ws = new WebSocket(url)
      wsRef.current = ws
    } catch {
      return
    }

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'subscribe' }))
    }

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string)
        if (data.type === 'session_updated') {
          // Future: invalidate edit-session query
        }
      } catch {
        /* ignore */
      }
    }

    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)

    return () => {
      clearInterval(ping)
      ws.close()
      wsRef.current = null
    }
  }, [sessionId, enabled])
}
