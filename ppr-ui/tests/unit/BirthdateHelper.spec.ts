import { describe, expect, it } from 'vitest'
import '@/composables' // load the barrel first so its import cycle resolves as in the app
import { useParty } from '@/composables/useParty'
import type { PartyIF } from '@/interfaces'
import {
  buildBirthdate,
  formatBirthdate,
  getBirthdateParts,
  isValidCalendarDate
} from '@/utils/birthdate-helper'

// Note: these helpers only use the YYYY-MM-DD part of the string, never the browser time zone,
// so they behave the same regardless of where the user is or what time it is when they save.

const { getDay, getFormattedBirthdate, getMonth, getMonthFull, getYear } = useParty()
const party = (birthDate: string): PartyIF => ({ birthDate } as PartyIF)

describe('birthdate helpers', () => {
  it('builds the entered date unchanged', () => {
    expect(buildBirthdate(1980, 3, 15)).toBe('1980-03-15T00:00:00-08:00')
    expect(buildBirthdate(1980, 12, 31)).toBe('1980-12-31T00:00:00-08:00')
    expect(buildBirthdate(1990, 1, 1)).toBe('1990-01-01T00:00:00-08:00')
  })

  it('rejects dates that do not exist instead of rolling them over', () => {
    expect(buildBirthdate(1980, 2, 31)).toBeNull()
    expect(buildBirthdate(1981, 2, 29)).toBeNull()
    expect(buildBirthdate(1980, 4, 31)).toBeNull()
    expect(buildBirthdate(1980, 2, 29)).toBe('1980-02-29T00:00:00-08:00')
    expect(buildBirthdate(NaN, 1, 1)).toBeNull()
    expect(buildBirthdate(1980, 0, 1)).toBeNull()
  })

  it('validates calendar dates', () => {
    expect(isValidCalendarDate(2000, 2, 29)).toBe(true)
    expect(isValidCalendarDate(1900, 2, 29)).toBe(false)
    expect(isValidCalendarDate(1980, 6, 31)).toBe(false)
    expect(isValidCalendarDate(1980, 13, 1)).toBe(false)
  })

  it('reads an API birthdate (UTC) back as the same calendar date', () => {
    // what the API returns for 1980-03-15T00:00:00-08:00
    const p = party('1980-03-15T08:00:00+00:00')
    expect(getYear(p)).toBe('1980')
    expect(getMonth(p)).toBe(3)
    expect(getMonthFull(p)).toBe('March')
    expect(getDay(p)).toBe('15')
    expect(getFormattedBirthdate(p)).toBe('March 15, 1980')
    expect(formatBirthdate(p.birthDate)).toBe('March 15, 1980')
  })

  it('reads the date prefix regardless of time or offset', () => {
    expect(getBirthdateParts('1990-07-01T08:00:00+00:00')).toEqual({ year: 1990, month: 7, day: 1 })
    expect(getBirthdateParts('1990-07-01T00:00:00-08:00')).toEqual({ year: 1990, month: 7, day: 1 })
    expect(getBirthdateParts('2026-11-20T08:00:00+00:00')).toEqual({ year: 2026, month: 11, day: 20 })
  })

  it('reads a date-only birthdate as-is', () => {
    expect(getBirthdateParts('1980-01-01')).toEqual({ year: 1980, month: 1, day: 1 })
  })

  it('round-trips build -> API -> read -> build (amendment comparison)', () => {
    const sent = buildBirthdate(2001, 11, 30)
    const fromApi = new Date(sent).toISOString().replace('.000Z', '+00:00')
    const parts = getBirthdateParts(fromApi)
    expect(parts).toEqual({ year: 2001, month: 11, day: 30 })
    expect(buildBirthdate(parts.year, parts.month, parts.day)).toBe(sent)
  })

  it('returns undefined when there is no birthdate', () => {
    const p = party('')
    expect(getFormattedBirthdate(p)).toBeUndefined()
    expect(getDay(p)).toBeUndefined()
    expect(getMonth(p)).toBeUndefined()
    expect(getMonthFull(p)).toBeUndefined()
    expect(getYear(p)).toBeUndefined()
    expect(formatBirthdate(undefined)).toBeUndefined()
  })
})
