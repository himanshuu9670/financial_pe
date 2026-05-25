import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE = __ENV.API_BASE || 'http://localhost:8000/api/v1'
const ROOT = BASE.replace('/api/v1', '')

export const options = {
  scenarios: {
    health_burst: {
      executor: 'constant-vus',
      vus: 20,
      duration: '45s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.15'],
  },
}

export default function () {
  const health = http.get(`${BASE}/health`)
  check(health, { 'health': (r) => r.status === 200 })

  const status = http.get(`${BASE}/system-status`)
  check(status, { 'system-status': (r) => r.status === 200 })

  const metrics = http.get(`${ROOT}/metrics`)
  check(metrics, { 'metrics': (r) => r.status === 200 })

  sleep(0.5)
}
