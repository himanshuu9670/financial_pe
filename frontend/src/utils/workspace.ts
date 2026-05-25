import type { ChangeType, FieldCoordinate, LedgerEntry } from '@/types/editSession'

export function fmtAmount(val: string | number | null | undefined): string {
  if (val == null || val === '') return ''
  const n = Number(val)
  if (Number.isNaN(n)) return String(val)
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function fieldValue(entry: LedgerEntry, field: ChangeType): string {
  const v = entry[field as keyof LedgerEntry]
  if (v == null) return ''
  return fmtAmount(v as string | number)
}

export function getFieldCoordinate(
  entry: LedgerEntry,
  field: ChangeType,
): FieldCoordinate | null {
  const coords = entry.coordinates
  if (!coords) return null
  const c = coords[field as keyof typeof coords]
  return c ?? null
}

export function editableFields(entry: LedgerEntry): ChangeType[] {
  const out: ChangeType[] = []
  if (getFieldCoordinate(entry, 'debit') || entry.debit != null) out.push('debit')
  if (getFieldCoordinate(entry, 'credit') || entry.credit != null) out.push('credit')
  if (getFieldCoordinate(entry, 'balance') || entry.balance != null) out.push('balance')
  return out
}

export function filterEntries(
  entries: LedgerEntry[],
  query: string,
): LedgerEntry[] {
  const q = query.trim().toLowerCase()
  if (!q) return entries
  return entries.filter(
    (e) =>
      e.description.toLowerCase().includes(q) ||
      String(e.debit ?? '').includes(q) ||
      String(e.credit ?? '').includes(q) ||
      (e.date ?? '').toLowerCase().includes(q),
  )
}
