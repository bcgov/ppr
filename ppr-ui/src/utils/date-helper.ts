import moment from 'moment'

/** Converts date to display format. */
export function convertDate (date: Date): string {
  // add 'Pacific Time' to end if pacific timezone
  let timezone = ''
  if ((date.toString()).includes('Pacific')) timezone = 'Pacific Time'

  // format datetime -- have to put in zeros manually when needed
  let hour = `0${date.getHours()}`
  let min = `0${date.getMinutes()}`
  let sec = `0${date.getSeconds()}`
  if (hour.length > 2) hour = hour.slice(1)
  if (min.length > 2) min = min.slice(1)
  if (sec.length > 2) sec = sec.slice(1)
  const datetime = `${hour}:${min}:${sec}`

  return moment(date).format('MMMM D, Y') + ` ${datetime} ${timezone}`
}
