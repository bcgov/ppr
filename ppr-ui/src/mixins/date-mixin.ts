import { Component, Mixins } from 'vue-property-decorator'
import { Getter } from 'vuex-class'
import { isDate } from 'lodash'
import { CommonMixin } from '@/mixins'

/**
 * Mixin that provides some useful date utilities.
 */
@Component({})
export default class DateMixin extends Mixins(CommonMixin) {
  /**
   * Fetches and returns the web server's current date (in UTC).
   * Used to bypass the user's local clock/timezone.
   * Ref: https://www.npmjs.com/package/serverdate
   * @returns a promise to return a Date object
   */
  async getServerDate (): Promise<Date> {
    const input = `${window.location.origin}/${process.env.VUE_APP_PATH}/`
    const init: RequestInit = { cache: 'no-store', method: 'HEAD' }

    // don't call fetch() during Jest tests
    // because it's not defined
    if (this.isJestRunning) return new Date()

    try {
      const { headers, ok, statusText } = await fetch(input, init)
      if (!ok) throw new Error(statusText)
      return new Date(headers.get('Date'))
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('Unable to get server date - using browser date instead')
      // fall back to local date
      // NB: new filings may contain invalid date/time
      return new Date()
    }
  }

  /**
   * Creates and returns a new Date object in UTC, given parameters in Pacific timezone.
   * (This works regardless of user's local clock/timezone.)
   * @example "2021, 0, 1, 0, 0" -> "2021-01-01T08:00:00.000Z"
   * @example "2021, 6, 1, 0, 0" -> "2021-07-01T07:00:00.000Z"
   */
  createUtcDate (year: number, month: number, day: number, hours: number = 0, minutes: number = 0): Date {
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
  yyyyMmDdToDate (dateStr: string): Date {
    // safety checks
    if (!dateStr) return null
    if (dateStr.length !== 10) return null

    const split = dateStr.split('-')
    const year = +split[0]
    const month = +split[1]
    const day = +split[2]

    return this.createUtcDate(year, (month - 1), day)
  }

  /**
   * Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
   * @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
   * @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
   */
  dateToYyyyMmDd (date: Date): string {
    // safety check
    if (!isDate(date) || isNaN(date.getTime())) return null

    const dateStr = date.toLocaleDateString('en-CA', {
      timeZone: 'America/Vancouver',
      month: 'numeric', // 12
      day: 'numeric', // 31
      year: 'numeric' // 2020
    })

    return dateStr
  }

  /**
   * Converts a date string (YYYY-MM-DD) to a date string (Month Day, Year) in Pacific timezone.
   * @param longMonth whether to show long month name (eg, December vs Dec)
   * @param showWeekday whether to show the weekday name (eg, Thursday)
   * @example "2021-01-01" -> "Thursday, December 31, 2020"
   */
  yyyyMmDdToPacificDate (dateStr: string, longMonth = false, showWeekday = false): string {
    return this.dateToPacificDate(this.yyyyMmDdToDate(dateStr), longMonth, showWeekday)
  }

  /**
   * Converts a Date object to a date string (Month Day, Year) in Pacific timezone.
   * @param longMonth whether to show long month name (eg, December vs Dec)
   * @param showWeekday whether to show the weekday name (eg, Thursday)
   * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020"
   * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021"
   */
  dateToPacificDate (date: Date, longMonth = false, showWeekday = false): string {
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
   * Converts a Date object to a time string (HH:MM am/pm) in Pacific timezone.
   * @example "2021-01-01 07:00:00 GMT" -> "11:00 pm"
   * @example "2021-01-01 08:00:00 GMT" -> "12:00 am"
   */
  dateToPacificTime (date: Date): string {
    // safety check
    if (!isDate(date) || isNaN(date.getTime())) return null

    let timeStr = date.toLocaleTimeString('en-CA', {
      timeZone: 'America/Vancouver',
      hour: 'numeric', // 11
      minute: '2-digit', // 00
      hour12: true // a.m./p.m.
    })

    // replace a.m. with am and p.m. with pm
    timeStr = timeStr.replace('a.m.', 'am').replace('p.m.', 'pm')

    return timeStr
  }

  /**
   * Converts a Date object to a date and time string (Month Day, Year at HH:MM am/pm
   * Pacific time).
   * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020 at 11:00 pm Pacific time"
   * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021 at 12:00 pm Pacific time"
   */
  dateToPacificDateTime (date: Date): string {
    // safety check
    if (!isDate(date) || isNaN(date.getTime())) return null

    const dateStr = this.dateToPacificDate(date, true)
    const timeStr = this.dateToPacificTime(date)

    return `${dateStr} at ${timeStr} Pacific time`
  }

  /**
   * Converts an API datetime string (in UTC) to a Date object.
   * @example 2021-08-05T16:56:50.783101+00:00 -> 2021-08-05T16:56:50Z
   */
  apiToDate (dateTimeString: string): Date {
    if (!dateTimeString) return null // safety check

    // chop off the milliseconds and UTC offset and append "Zulu" timezone abbreviation
    dateTimeString = dateTimeString.slice(0, 19) + 'Z'

    return new Date(dateTimeString)
  }

  /**
   * Converts an API datetime string (in UTC) to a date and time string (Month Day, Year at HH:MM am/pm
   * Pacific time).
   * @example "2021-01-01T00:00:00.000000+00:00" -> "Dec 31, 2020 at 04:00 pm Pacific time" (PST example)
   * @example "2021-07-01T00:00:00.000000+00:00" -> "Jun 30, 2021 at 05:00 pm Pacific time" (PDT example)
   */
  apiToPacificDateTime (dateTimeString: string): string {
    if (!dateTimeString) return null // safety check

    const date = this.apiToDate(dateTimeString)
    const dateStr = this.dateToPacificDate(date)
    const timeStr = this.dateToPacificTime(date)

    return `${dateStr} at ${timeStr} Pacific time`
  }

  /**
   * Converts a Date object to an API datetime string.
   * @example 2021-08-05T16:56:50Z -> 2021-08-05T16:56:50+00:00
   */
  dateToApi (date: Date): string {
    // safety check
    if (!isDate(date) || isNaN(date.getTime())) return null

    // replace "Zulu" timezone abbreviation with UTC offset
    return date.toISOString().replace('Z', '+00:00')
  }
}
