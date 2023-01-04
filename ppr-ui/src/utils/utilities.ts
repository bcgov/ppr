export function isSigningIn (): boolean {
  const path = window.location.pathname
  return path.includes('/login') || path.includes('/signin')
}

export function isSigningOut (): boolean {
  const path = window.location.pathname
  return path.includes('/signout')
}

export function addTimestampToDate (dateToConvert: string, isEndDate: boolean): string {
  if (dateToConvert.length < 11) {
    // convert to local date object
    const d = new Date(`${dateToConvert}T00:00:00`)
    // get the offset from utc in hours
    let offset = `${d.getTimezoneOffset() / 60}`
    let tzDiff = '-'
    if (offset[0] === '-') {
      // flip tzDiff and remove negative from offset
      tzDiff = '+'
      offset = offset.substring(1, offset.length)
    }
    // check if offset has minutes
    const minsIndex = offset.indexOf('.')
    if (minsIndex !== -1) {
      // remove the minutes from the offset (not perfect but better than an error)
      offset = offset.substring(0, minsIndex)
    }
    // add zero to offset if necessary
    if (offset.length < 2) offset = `0${offset}`
    // add desired timestamp
    let time = '00:00:00'
    if (isEndDate) time = '23:59:59'
    // combine date, timestamp and tz info
    dateToConvert = `${d.toISOString().substring(0, 10)}T${time}${tzDiff}${offset}:00`
  }
  return dateToConvert
}
