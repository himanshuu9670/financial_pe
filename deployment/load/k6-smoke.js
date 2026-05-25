import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE = __ENV.API_BASE || 'http://localhost:8000/api/v1'

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.1'],
  },
}

export default function () {
  const health = http.get(`${BASE.replace('/api/v1', '')}/api/v1/health`)
  check(health, { 'health ok': (r) => r.status === 200 })
  const status = http.get(`${BASE}/system-status`)
  check(status, { 'system status': (r) => r.status === 200 })
  sleep(1)
}
