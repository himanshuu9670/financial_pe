import type { TextBlock, TextSpan } from '@/types/extraction'

export interface ViewportRect {
  left: number
  top: number
  width: number
  height: number
}

/** Map PDF bbox (top-left origin) to overlay pixels at render scale. */
export function pdfBboxToViewport(
  bbox: [number, number, number, number],
  scale: number,
  offsetX = 0,
  offsetY = 0,
): ViewportRect {
  const [x0, y0, x1, y1] = bbox
  return {
    left: x0 * scale + offsetX,
    top: y0 * scale + offsetY,
    width: (x1 - x0) * scale,
    height: (y1 - y0) * scale,
  }
}

export function normalizeBbox(
  bbox: [number, number, number, number],
  pageWidth: number,
  pageHeight: number,
): [number, number, number, number] {
  return [
    bbox[0] / pageWidth,
    bbox[1] / pageHeight,
    bbox[2] / pageWidth,
    bbox[3] / pageHeight,
  ]
}

export function blockLabel(block: TextBlock | TextSpan): string {
  const b = block as TextBlock
  if ('font' in b && b.font) {
    return `${b.text.slice(0, 40)}${b.text.length > 40 ? '…' : ''} · ${b.font} ${b.font_size}pt`
  }
  const s = block as TextSpan
  return `${s.text} · (${s.x}, ${s.y}) · ${s.font} ${s.font_size}pt`
}
