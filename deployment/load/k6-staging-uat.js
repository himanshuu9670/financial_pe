import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE = __ENV.API_BASE || 'http://localhost/api/v1'
const TOKEN = __ENV.UAT_TOKEN || ''

const headers = TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}

export const options = {
  scenarios: {
    health_steady: {
      executor: 'constant-vus',
      vus: 10,
      duration: '2m',
    },
    burst: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 25 },
        { duration: '1m', target: 25 },
        { duration: '30s', target: 0 },
      ],
      startTime: '2m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<4000'],
    http_req_failed: ['rate<0.2'],
  },
}

export default function () {
  const health = http.get(`${BASE}/health`, { headers })
  check(health, { health: (r) => r.status === 200 })

  const status = http.get(`${BASE}/system-status`, { headers })
  check(status, { system: (r) => r.status === 200 })

  if (TOKEN) {
    const ai = http.get(`${BASE}/ai/status`, { headers })
    check(ai, { ai: (r) => r.status === 200 || r.status === 404 })
  }

  sleep(0.3)
}
