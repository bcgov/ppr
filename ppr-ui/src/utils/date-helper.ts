import moment, { Moment } from 'moment'
import 'moment-timezone'
import { isDate } from 'lodash'

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

/**
 * Converts a date string in 'YYYY-MM-DD' format to a long date format, ignoring the timezone.
 *
 * @example "2024-05-20" -> "May 20, 2024"
 * @param dateString - A string representing a date in 'YYYY-MM-DD' format.
 * @returns A string representing the date in long format.
 * @throws Will throw an error if the date string is not in 'YYYY-MM-DD' format.
 */
export function convertDateToLongFormat (dateString: string): string {
  const [year, month, day] = dateString.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
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
  let pacificDate = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'long',
    timeStyle: omitSeconds ? 'short' : 'medium',
    timeZone: 'America/Vancouver',
    hour12: true
  })
    .format(new Date(date))

  // Convert AM/PM to lowercase
  pacificDate = pacificDate.replace('AM', 'am')
  pacificDate = pacificDate.replace('PM', 'pm')

  return `${pacificDate} Pacific time`
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
 * Takes a pacific time and creates a new date adjusted to user localtime.
 * (This works regardless of user's local clock/timezone.)
 */
export function createDateFromPacificTime (year: number, month: number, day: number,
  hours: number = 0, minutes: number = 0): Date {
  // FUTURE: change this to get the date from the server
  const currUserTime = new Date()
  const currPacificTime = new Date(currUserTime.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))

  // Handle extremely rare race condition if minute changed between the two calls above
  // This interval should be more than sufficient to catch this race condition
  if (currUserTime.getSeconds() >= 57 && currPacificTime.getSeconds() <= 3) {
    // Try again condition should not occur again
    return createDateFromPacificTime(year, month, day, hours, minutes)
  }

  // Zero out seconds and milliseconds
  currUserTime.setSeconds(0, 0)
  currPacificTime.setSeconds(0, 0)

  // Difference between current time zone to pacific time zone
  const timeZoneDiff = currUserTime.getTime() - currPacificTime.getTime()

  // Date object is always set to the localtime zone in javascript
  const adjustedDateObject = new Date(new Date(year, month, day, hours, minutes).getTime() + timeZoneDiff)

  return adjustedDateObject
}

/**
 * Converts a date string (YYYY-MM-DD) to a Date object at 12:00:00 am Pacific time.
 * @example 2021-11-22 -> 2021-11-22T00:00:00.00 Pacific Time
 */
export function yyyyMmDdToDate (dateStr: string): Date {
  // safety checks
  if (!dateStr) return null
  if (dateStr.length !== 10) return null

  const split = dateStr.split('-')
  const year = +split[0]
  const month = +split[1]
  const day = +split[2]

  return createDateFromPacificTime(year, (month - 1), day)
}

/**
 * Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
 * @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
 * @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
 */
export function dateToYyyyMmDd (date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null
  const localDate = date.toLocaleDateString('en-CA', {
    timeZone: 'America/Vancouver',
    month: 'numeric', // 12
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })

  return convertDateFormat(localDate)
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
