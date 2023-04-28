import moment, { Moment } from 'moment'
import 'moment-timezone'
import { isDate } from 'lodash'

/** returns timstamp string in 12 hour format */
export function format12HourTime (date: Date): string {
  // format datetime -- have to put in zeros manually when needed
  let hours = date.getHours()
  const ampm = hours < 12 ? 'am' : 'pm'
  hours = hours < 12 ? hours : hours - 12
  hours = hours !== 0 ? hours : 12

  let min = `0${date.getMinutes()}`
  let sec = `0${date.getSeconds()}`
  if (min.length > 2) min = min.slice(1)
  if (sec.length > 2) sec = sec.slice(1)

  return `${hours}:${min}:${sec} ${ampm}`
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
export function convertDate (date: Date, includeTime: boolean, includeTz: boolean): string {
  if (!includeTime) return moment(date).format('MMMM D, Y')

  // add 'Pacific Time' to end if pacific timezone
  let timezone = ''
  if ((date.toString()).includes('Pacific')) timezone = 'Pacific time'

  const datetime = format12HourTime(date)

  if (includeTz) return moment(date).format('MMMM D, Y') + ` at ${datetime} ${timezone}`
  else return moment(date).format('MMMM D, Y') + ` ${datetime}`
}

export function pacificDate (date: Date): string {
  date = new Date(date.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
  const datetime = format12HourTime(date)

  return moment(date).format('MMMM D, Y') + ` at ${datetime} Pacific time`
}

export function tzOffsetMinutes (date: Date): number {
  let offset = 8 * 60
  if (moment(date).isDST()) {
    offset = 7 * 60
  }
  return offset
}

export function isInt (intValue) {
  if (isNaN(intValue)) {
    return false
  }
  const x = parseFloat(intValue)
  return (x | 0) === x
}

/**
 * Creates and returns a new Date object in UTC, given parameters in Pacific timezone.
 * (This works regardless of user's local clock/timezone.)
 * @example "2021, 0, 1, 0, 0" -> "2021-01-01T08:00:00.000Z"
 * @example "2021, 6, 1, 0, 0" -> "2021-07-01T07:00:00.000Z"
 */
export function createUtcDate (year: number, month: number, day: number, hours: number = 0, minutes: number = 0): Date {
  // FUTURE: change this to get the date from the server
  const jsDate = new Date()
  const date = new Date(jsDate.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))

  // update all date and time fields
  date.setFullYear(year, month, day)
  date.setHours(hours, minutes, 0, 0) // zero out seconds and milliseconds

  return date
}

/**
 * Converts a date string (YYYY-MM-DD) to a Date object at 12:00:00 am Pacific time.
 * @example 2021-11-22 -> 2021-11-22T08:00:00.00Z
 */
export function yyyyMmDdToDate (dateStr: string): Date {
  // safety checks
  if (!dateStr) return null
  if (dateStr.length !== 10) return null

  const split = dateStr.split('-')
  const year = +split[0]
  const month = +split[1]
  const day = +split[2]

  return createUtcDate(year, (month - 1), day)
}

/**
 * Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
 * @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
 * @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
 */
export function dateToYyyyMmDd (date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  return date.toLocaleDateString('en-CA', {
    timeZone: 'America/Vancouver',
    month: 'numeric', // 12
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })
}

/**
 * Converts a date string (YYYY-MM-DD) to a date string (Month Day, Year) in Pacific timezone.
 * @param longMonth whether to show long month name (eg, December vs Dec)
 * @param showWeekday whether to show the weekday name (eg, Thursday)
 * @example "2021-01-01" -> "Thursday, December 31, 2020"
 */
export function yyyyMmDdToPacificDate (dateStr: string, longMonth = false, showWeekday = false): string {
  return dateToPacificDate(yyyyMmDdToDate(dateStr), longMonth, showWeekday)
}

/**
 * Converts a Date object to a date string (Month Day, Year) in Pacific timezone.
 * @param longMonth whether to show long month name (eg, December vs Dec)
 * @param showWeekday whether to show the weekday name (eg, Thursday)
 * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020"
 * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021"
 */
export function dateToPacificDate (date: Date, longMonth = false, showWeekday = false): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  let dateStr = date.toLocaleDateString('en-CA', {
    timeZone: 'America/Vancouver',
    weekday: showWeekday ? 'long' : undefined, // Thursday or nothing
    month: longMonth ? 'long' : 'short', // December or Dec
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })

  // remove period after month
  dateStr = dateStr.replace('.', '')

  return dateStr
}

export function localTodayDate (date: Date = new Date()): string {
  const localYear = date.toLocaleDateString('en-CA', { year: 'numeric', timeZone: 'America/Vancouver' })
  const localMonth = date.toLocaleDateString('en-CA', { month: '2-digit', timeZone: 'America/Vancouver' })
  const localDay = date.toLocaleDateString('en-CA', { day: '2-digit', timeZone: 'America/Vancouver' })
  return [localYear, localMonth, localDay].join('-')
}
