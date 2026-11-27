import type { Moment } from 'moment';
import moment from 'moment'
import type { CalendarDate } from '@internationalized/date'
import { today } from '@internationalized/date'

const date = new Date()

/** returns timstamp string in 12 hour format */
export function format12HourTime (date: Date, omitSeconds = false): string {
  // format datetime -- have to put in zeros manually when needed
  let hours = date.getHours()
  const ampm = hours < 12 ? 'am' : 'pm'
  hours = hours < 12 ? hours : hours - 12
  hours = hours !== 0 ? hours : 12

  let min = `0${date.getMinutes()}`
  let sec = `0${date.getSeconds()}`
  if (min.length > 2) min = min.slice(1)
  if (sec.length > 2) sec = sec.slice(1)

  return omitSeconds
    ? `${hours}:${min} ${ampm}`
    : `${hours}:${min}:${sec} ${ampm}`
}

export function format12HourTimeMoment (date: Moment): string {
  return date.format('h:mm:ss a')
}

export function formatExpiryDate (expDate: Date) {
  const date = moment(expDate)
  // if savings time in future is different, adjust
  if (date.format('h') === '12') {
    date.subtract(1, 'hour')
  }
  if (date.format('h') === '10') {
    date.add(1, 'hour')
  }
  const datetime = format12HourTimeMoment(date)
  return moment(date).format('MMMM D, Y') + ` at ${datetime} Pacific time`
}

/** Converts date to display format. */
export function convertDate (date: Date|string, includeTime: boolean, includeTz: boolean): string {
  if (!includeTime) return moment(date).format('MMMM D, Y')

  // add 'Pacific Time' to end if pacific timezone
  let timezone = ''
  if ((date.toString()).includes('Pacific')) timezone = 'Pacific time'

  const datetime = format12HourTime(date as Date)

  if (includeTz) return moment(date).format('MMMM D, Y') + ` at ${datetime} ${timezone}`
  else return moment(date).format('MMMM D, Y') + ` ${datetime}`
}

// Converts date to string and pacific date string
// Example Output: August 11, 2023
export function shortPacificDate (date: Date | string): string {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'long',
    timeZone: 'America/Vancouver'
  }).format(new Date(date))
}

// Converts date to string and pacific time
// Example Output: August 11, 2023 at 10:38 AM
export function pacificDate (date: Date | string, omitSeconds = false): string {
  // Build from parts: the date/time separator (' at ' vs ', ') differs between browsers and the Intl polyfill
  const parts = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: omitSeconds ? undefined : '2-digit',
    timeZone: 'America/Vancouver',
    hour12: true
  }).formatToParts(new Date(date))
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find(p => p.type === type)?.value

  const time = omitSeconds
    ? `${part('hour')}:${part('minute')}`
    : `${part('hour')}:${part('minute')}:${part('second')}`

  // Convert AM/PM to lowercase
  return `${part('month')} ${part('day')}, ${part('year')} at ${time} ${part('dayPeriod')?.toLowerCase()} Pacific time`
}

export function isInt (intValue) {
  if (isNaN(intValue)) {
    return false
  }
  const x = parseFloat(intValue)
  return (x | 0) === x
}

/*
 * Calendar dates (YYYY-MM-DD): a day, not a moment in time, eg a birthdate or a date entered in a date picker.
 * They are handled as plain year/month/day and never converted through a time zone, so they show the same
 * date for every user. When the API needs a date time string, use addTimestampToDate.
 */

export interface CalendarDatePartsIF {
  year: number
  month: number // 1-12
  day: number
}

/** True if year/month/day form a real calendar date (rejects e.g. Feb 30, Apr 31). */
export function isValidCalendarDate (year: number, month: number, day: number): boolean {
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) return false
  if (month < 1 || month > 12 || day < 1) return false
  return day <= new Date(Date.UTC(year, month, 0)).getUTCDate()
}

/**
 * Year/month/day of a 'YYYY-MM-DD' date string, or null if it isn't a real date.
 * Only a date string is accepted: to use the date of an API timestamp, pass its date part explicitly.
 */
export function parseYyyyMmDd (dateStr: string): CalendarDatePartsIF {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr || '')
  if (!match) return null
  const [year, month, day] = match.slice(1).map(Number)
  return isValidCalendarDate(year, month, day) ? { year, month, day } : null
}

/**
 * Formats a date string (YYYY-MM-DD) for display, or '' if it isn't a real date.
 * @param longMonth whether to show long month name (eg, December vs Dec)
 * @param showWeekday whether to show the weekday name (eg, Thursday)
 * @example "2020-12-31" -> "Dec 31, 2020"
 * @example "2020-12-31", longMonth -> "December 31, 2020"
 * @example "2020-12-31", longMonth, showWeekday -> "Thursday, December 31, 2020"
 */
export function formatCalendarDate (dateStr: string, longMonth = false, showWeekday = false): string {
  const parts = parseYyyyMmDd(dateStr)
  if (!parts) return ''
  // the date is built and formatted in UTC, so no time zone can move it to another day
  return new Date(Date.UTC(parts.year, parts.month - 1, parts.day)).toLocaleDateString('en-CA', {
    timeZone: 'UTC',
    weekday: showWeekday ? 'long' : undefined, // Thursday or nothing
    month: longMonth ? 'long' : 'short', // December or Dec
    day: 'numeric', // 31
    year: 'numeric' // 2020
  }).replace('.', '') // remove period after short month (eg, Dec.)
}

/** Month name for a 1-based month, in en-CA. */
export function getMonthName (month: number): string {
  return new Date(Date.UTC(2000, month - 1, 1)).toLocaleString('en-CA', { month: 'long', timeZone: 'UTC' })
}

/**
 * Adds days to a date string (YYYY-MM-DD), returning a date string, or null if it isn't a real date.
 * @example "2026-12-15", 30 -> "2027-01-14"
 */
export function addDaysToYyyyMmDd (dateStr: string, daysToAdd: number): string {
  const parts = parseYyyyMmDd(dateStr)
  if (!parts) return null
  // Date.UTC rolls the day over into the next month/year as needed
  return new Date(Date.UTC(parts.year, parts.month - 1, parts.day + daysToAdd)).toISOString().substring(0, 10)
}

/**
 * Adds a start of day time to a date string (YYYY-MM-DD) for the API, eg, for a birthdate or
 * unit note effective date. The result is on that same date in Pacific time.
 * Values that are not a date string (eg, already have a time) are returned unchanged.
 *
 * Pacific time is always UTC-8 or UTC-7 (PST, PDT, or the permanent UTC-7 since Nov 1, 2026), so
 * -08:00 is 00:00 (UTC-8) or 01:00 (UTC-7) on that date: the Pacific date is the date that was entered,
 * for any year, with no offset calculation.
 * @example "2023-07-01" -> "2023-07-01T00:00:00-08:00"
 */
export function addTimestampToDate (dateToConvert: string): string {
  if (!parseYyyyMmDd(dateToConvert)) return dateToConvert
  return `${dateToConvert}T00:00:00-08:00`
}

/**
 * Adds the start or end of day time to a date string (YYYY-MM-DD) for a registration date range filter.
 * The APIs treat Pacific time as a fixed UTC-7, so -07:00 gives their exact 00:00:00 or 23:59:59 on that date.
 * Values that are not a date string (eg, already have a time) are returned unchanged.
 * @example "2026-11-20" -> "2026-11-20T00:00:00-07:00"
 * @example "2026-11-20", end of day -> "2026-11-20T23:59:59-07:00"
 */
export function addFilterTimestampToDate (dateToConvert: string, isEndDate = false): string {
  if (!parseYyyyMmDd(dateToConvert)) return dateToConvert
  return `${dateToConvert}${isEndDate ? 'T23:59:59' : 'T00:00:00'}-07:00`
}

/*
 * Birthdates are calendar dates:
 * - Sending: build the string straight from the entered year/month/day (addTimestampToDate).
 * - Reading: use the 'YYYY-MM-DD' date part of the string the API returns.
 * The UI sends 'YYYY-MM-DDT00:00:00-08:00'; the API stores and returns it as
 * 'YYYY-MM-DDT08:00:00+00:00', so the date part is always the date that was entered.
 */

/** Build the API birthdate string from the entered date, or null if it isn't a real date. */
export function buildBirthdate (year: number, month: number, day: number): string {
  if (!isValidCalendarDate(year, month, day)) return null
  const pad = (n: number, len = 2) => String(n).padStart(len, '0')
  return addTimestampToDate(`${pad(year, 4)}-${pad(month)}-${pad(day)}`)
}

/** Year/month/day of an API birthdate (its 'YYYY-MM-DD' date part), or null. */
export function getBirthdateParts (birthDate: string): CalendarDatePartsIF {
  return parseYyyyMmDd(birthDate?.substring(0, 10))
}

/** e.g. 'March 15, 1980', or undefined if there is no valid birthdate. */
export function formatBirthdate (birthDate: string): string {
  return formatCalendarDate(birthDate?.substring(0, 10), true) || undefined
}

/**
 * Converts a date string (YYYY-MM-DD) to a Date object on that date in Pacific time (eg, for a date picker).
 * @example 2021-11-22 -> 2021-11-22T00:00:00-08:00
 */
export function yyyyMmDdToDate (dateStr: string): Date {
  return parseYyyyMmDd(dateStr) ? new Date(addTimestampToDate(dateStr)) : null
}

/**
 * Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
 * @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
 * @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
 */
export function dateToYyyyMmDd (date: Date): string {
  // safety check
  if (!(date instanceof Date) || isNaN(date.getTime())) return null
  const localDate = date.toLocaleDateString('en-CA', {
    timeZone: 'America/Vancouver',
    month: 'numeric', // 12
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })

  return convertDateFormat(localDate)
}

/**
 * Transforms a date string from "YYYY/MM/DD" to "YYYY-MM-DD" format.
 * Useful for modern versions of safari where date functions can return non-iso formats
 * @param dateString
 */
export function convertDateFormat(dateString) {
  const originalDate = new Date(dateString)

  // Check if the date is valid and the input format is "MM/DD/YYYY"
  if (!isNaN(originalDate.getTime()) && /\d{1,2}\/\d{1,2}\/\d{4}/.test(dateString)) {
    const year = originalDate.getFullYear()
    const month = (originalDate.getMonth() + 1).toString().padStart(2, '0')
    const day = originalDate.getDate().toString().padStart(2, '0')

    return `${year}-${month}-${day}`
  }

  // If the date is already in "YYYY-MM-DD" format or invalid, return the original input
  return dateString
}

export function localTodayDate (date: Date = new Date(), returnYYYYMMDD: boolean = false): string {
  const localYear = date.toLocaleDateString('en-CA', { year: 'numeric', timeZone: 'America/Vancouver' })
  const localMonth = date.toLocaleDateString('en-CA', { month: '2-digit', timeZone: 'America/Vancouver' })
  const localDay = date.toLocaleDateString('en-CA', { day: '2-digit', timeZone: 'America/Vancouver' })
  if (returnYYYYMMDD) return `${localYear}, ${localMonth}, ${localDay}`
  return [localYear, localMonth, localDay].join('-')
}

// util obj with various dates, e.g. for the DatePicker min and max dates
export const calendarDates = {
  tomorrow: localTodayDate(new Date(date.setDate(date.getDate() + 2))),
  endOfYear: localTodayDate(new Date(new Date().getFullYear(), 11, 31)),
  startOfNextYear: localTodayDate(new Date(new Date().getFullYear() + 1, 0, 1))
}

/**
 * Checks if the provided date and time is within a specified minute differential
 * compared to the current system time.
 *
 * @param {string} createDateTime - The date and time to compare in ISO 8601 format.
 * @param {number} minuteDifferential - The maximum allowed difference in minutes.
 * @returns {boolean} Returns true if the provided date and time is within the specified minute differential, otherwise
 * false.
 */
export const isWithinMinutes = (createDateTime: string, minuteDifferential: number) => {
  // Convert the provided createDateTime to a Date object
  const createTime: Date = new Date(createDateTime)

  // Calculate the difference in milliseconds between the createDateTime and current system time
  const timeDifference: number = new Date().getTime() - createTime.getTime()

  // Convert the time difference from milliseconds to minutes
  const minutesDifference: number = Math.abs(timeDifference / (1000 * 60))

  // Check if the time difference is within the specified minute differential
  return minutesDifference <= minuteDifferential
}

/**
 * Converts a date string to an ISO 8601 date-time string representing the last minute of the day.
 * @param {string} dateStr - The date string in the format 'YYYY-MM-DD'.
 * @returns {string} - An ISO 8601 date-time string representing the last minute of the specified day.
 * @example
 * Input:  2024-05-26
 * Output: 2024-05-26T23:59:59+00:00
 */
export function convertToISO8601LastMinute(dateStr: string): string {
  return `${dateStr}T23:59:59+00:00`
}

/**
 * This function calculates a previous date based on the given input format.
 * The input format is a string like 'd-7', 'm-3', or 'y-1', where:
 *  - 'd' stands for days (e.g., 'd-7' means 7 days ago)
 *  - 'm' stands for months (e.g., 'm-3' means 3 months ago)
 *  - 'y' stands for years (e.g., 'y-1' means 1 year ago)
 *
 * @param {string} input - A string representing the time offset. It follows the pattern 'd-N', 'm-N', or 'y-N'
 *
 * @returns {CalendarDate} - The calculated date based on the current date minus the provided time offset.
 */
export function calculatePreviousDate(input: string): CalendarDate {
  // Extract the unit (d, m, y) and the amount (number)
  const regex = /^([dmy])-([0-9]+)$/;
  const match = input.match(regex);

  if (!match) {
    throw new Error("Invalid input format. Expected format: d-7, m-3, y-1, etc.");
  }

  const unit = match[1];
  const amount = parseInt(match[2], 10);

  // Get today's date as a CalendarDate
  const currentDate = today();

  switch (unit) {
    case "d":
      return currentDate.subtract({ days: amount });
    case "m":
      return currentDate.subtract({ months: amount });
    case "y":
      return currentDate.subtract({ years: amount });
    default:
      throw new Error("Invalid unit. Use 'd' for days, 'm' for months, or 'y' for years.");
  }
}
