import { Component, Vue } from 'vue-property-decorator'

/**
 * Mixin that provides some useful date utilities.
 */
@Component({})
export default class DateMixin extends Vue {
  readonly MS_IN_A_DAY = (1000 * 60 * 60 * 24)

  /**
   * Converts a JavaScript date object to a simple date string.
   * @param date The date to convert.
   * @returns A simple date string formatted as YYYY-MM-DD.
   */
  dateToUsableString (date: Date): string | null{
    if (!date || date.toString() === 'Invalid Date') return null

    const yyyy = date.getFullYear().toString()
    const mm = (date.getMonth() + 1).toString().padStart(2, '0')
    const dd = date.getDate().toString().padStart(2, '0')

    return `${yyyy}-${mm}-${dd}`
  }

  /**
   * Formats a simple date string (YYYY-MM-DD) to (Month Day, Year) for readability.
   * @param date the date string to format
   * @returns the formatted date string
   */
  toReadableDate (date: string): string {
    // cast to a workable dateString
    // split into an array
    const formatDate = (new Date(date).toDateString()).split(' ')

    // remove the 'weekday' from the array
    // join the array
    // add a comma to the date output
    const regex = / (?!.* )/
    return formatDate.slice(1).join(' ').replace(regex, ', ')
  }

  /**
   * Converts a datetime from UTC to local (Pacific) timezone.
   * @param date the datetime string in UTC timezone
   * @returns the datetime string in local timezone
   */
  convertUtcTimeToLocalTime (dateString: string): string {
    if (!dateString) return null // safety check

    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
      timeZone: 'America/Vancouver'
    }

    // chop off the milliseconds and append "Zulu" timezone abbreviation
    // eg, 2020-08-28T21:53:58Z
    dateString = dateString.slice(0, 19) + 'Z'
    const date = new Date(dateString)

    // locale 'en-CA' is the only one consistent between IE11 and other browsers
    // example output: "2019-12-31 04:00 PM"
    let datetimeLocal = new Intl.DateTimeFormat('en-CA', options).format(date)

    // misc cleanup
    datetimeLocal = datetimeLocal.replace(', ', ' at ')
    datetimeLocal = datetimeLocal.replace('a.m.', 'AM')
    datetimeLocal = datetimeLocal.replace('p.m.', 'PM')

    // fix for Jest (which outputs MM/DD/YYYY no matter which 'en' locale is used)
    if (datetimeLocal.indexOf('/') >= 0) {
      const date = datetimeLocal.substr(0, 10).split('/')
      const time = datetimeLocal.slice(11)
      // set as YYYY-MM-DD HH:MM AM/PM
      datetimeLocal = `${date[2]}-${date[0]}-${date[1]} ${time}`
    }

    return datetimeLocal
  }
}
