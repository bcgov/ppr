/** Common Date Functions. **/
export const useDateHelper = () => {
  /**
   * Creates and returns a new Date object in UTC, given parameters in Pacific timezone.
   * (This works regardless of user's local clock/timezone.)
   * @example "2021, 0, 1, 0, 0" -> "2021-01-01T08:00:00.000Z"
   * @example "2021, 6, 1, 0, 0" -> "2021-07-01T07:00:00.000Z"
   */
  const createUtcDate = (year: number, month: number, day: number, hours: number = 0, minutes: number = 0): Date => {
    // FUTURE: change this to get the date from the server
    const jsDate = new Date()
    const date = new Date(jsDate.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))

    // update all date and time fields
    date.setFullYear(year, month, day)
    date.setHours(hours, minutes, 0, 0) // zero out seconds and milliseconds

    return date
  }

  /**
   * Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
   * @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
   * @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
   */
  const dateToYyyyMmDd = (date: Date): string => {
    return date.toLocaleDateString('en-CA', {
      timeZone: 'America/Vancouver',
      month: 'numeric', // 12
      day: 'numeric', // 31
      year: 'numeric' // 2020
    })
  }

  return {
    createUtcDate,
    dateToYyyyMmDd
  }
}
