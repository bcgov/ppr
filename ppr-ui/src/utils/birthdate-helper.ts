/**
 * Birthdates are calendar dates, so we never run them through the browser's time zone.
 * - Sending: build the string straight from the entered year/month/day.
 * - Reading: take the 'YYYY-MM-DD' prefix of the string the API returns.
 *
 * The UI sends 'YYYY-MM-DDT00:00:00-08:00'; the API stores and returns it as
 * 'YYYY-MM-DDT08:00:00+00:00', so the prefix is always the date that was entered.
 */

export interface BirthdatePartsIF {
  year: number
  month: number // 1-12
  day: number
}

/** True if year/month/day form a real calendar date (rejects e.g. Feb 30, Apr 31). */
export function isValidCalendarDate (year: number, month: number, day: number): boolean {
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) return false
  if (month < 1 || month > 12 || day < 1) return false
  return day <= new Date(Date.UTC(year, month, 0)).getUTCDate() // last day of the month
}

/** Build the API birthdate string from the entered date, or null if it isn't a real date. */
export function buildBirthdate (year: number, month: number, day: number): string {
  if (!isValidCalendarDate(year, month, day)) return null
  const pad = (n: number, len = 2) => String(n).padStart(len, '0')
  return `${pad(year, 4)}-${pad(month)}-${pad(day)}T00:00:00-08:00`
}

/** Year/month/day from the 'YYYY-MM-DD' prefix of an API birthdate. */
export function getBirthdateParts (birthDate: string): BirthdatePartsIF {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(birthDate || '')
  if (!match) return null
  const [year, month, day] = match.slice(1).map(Number)
  return isValidCalendarDate(year, month, day) ? { year, month, day } : null
}

/** Month name for a 1-based month, in en-CA. */
export function getMonthName (month: number): string {
  return new Date(Date.UTC(2000, month - 1, 1)).toLocaleString('en-CA', { month: 'long', timeZone: 'UTC' })
}

/** e.g. 'March 15, 1980' */
export function formatBirthdate (birthDate: string): string {
  const parts = getBirthdateParts(birthDate)
  return parts ? `${getMonthName(parts.month)} ${parts.day}, ${parts.year}` : undefined
}
