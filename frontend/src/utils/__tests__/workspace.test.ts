import { describe, expect, it } from 'vitest'
import { filterEntries, fmtAmount, fieldValue } from '@/utils/workspace'
import type { LedgerEntry } from '@/types/editSession'

const entry: LedgerEntry = {
  transaction_id: '1',
  row_index: 0,
  page: 1,
  date: '01/01/2024',
  description: 'UPI TEST',
  debit: '100',
  credit: null,
  balance: '9000',
  previous_balance: null,
  is_modified: false,
  propagation_affected: false,
  validation_warnings: [],
  row_bbox: [0, 0, 100, 12],
}

describe('workspace utils', () => {
  it('formats amounts', () => {
    expect(fmtAmount('5000')).toContain('5')
  })

  it('reads field values', () => {
    expect(fieldValue(entry, 'debit')).toBeTruthy()
  })

  it('filters by description', () => {
    expect(filterEntries([entry], 'upi')).toHaveLength(1)
    expect(filterEntries([entry], 'xyz')).toHaveLength(0)
  })
})
