import { describe, expect, it } from 'vitest'
import { pdfBboxToViewport } from '@/utils/coordinates'

describe('pdfBboxToViewport at zoom', () => {
  it('scales bbox linearly at 1x', () => {
    const r = pdfBboxToViewport([10, 20, 110, 32], 1)
    expect(r.left).toBe(10)
    expect(r.top).toBe(20)
    expect(r.width).toBe(100)
    expect(r.height).toBe(12)
  })

  it('scales bbox at 1.5x zoom', () => {
    const r = pdfBboxToViewport([10, 20, 110, 32], 1.5)
    expect(r.left).toBe(15)
    expect(r.width).toBe(150)
  })
})
