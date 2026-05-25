import { describe, expect, it } from 'vitest'
import { normalizeBbox, pdfBboxToViewport } from '@/utils/coordinates'

describe('Phase 2 coordinate mapping', () => {
  it('maps PDF bbox to viewport pixels at scale', () => {
    const rect = pdfBboxToViewport([100, 200, 150, 220], 1.5)
    expect(rect.left).toBe(150)
    expect(rect.top).toBe(300)
    expect(rect.width).toBe(75)
    expect(rect.height).toBe(30)
  })

  it('normalizes bbox to page fractions', () => {
    const norm = normalizeBbox([100, 200, 200, 400], 400, 800)
    expect(norm[0]).toBeCloseTo(0.25)
    expect(norm[1]).toBeCloseTo(0.25)
    expect(norm[2]).toBeCloseTo(0.5)
    expect(norm[3]).toBeCloseTo(0.5)
  })
})
