import moment, { Moment } from 'moment'
import 'moment-timezone'

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
  return date.format('h:m:s a')
}

export function formatExpiryDate (expDate: Date) {
  const date = moment(expDate).tz('America/Vancouver')
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
  var x = parseFloat(intValue)
  return (x | 0) === x
}
