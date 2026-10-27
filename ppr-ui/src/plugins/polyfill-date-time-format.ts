import { defineNuxtPlugin } from '#app'

/**
 * BC moved to permanent Pacific time (UTC-7) as of Nov 1, 2026 (tz rules updated 2026-09-29).
 * Browsers without the updated tz data still return UTC-8 for 'America/Vancouver' in winter,
 * so polyfill Intl.DateTimeFormat (and Date toLocale*String) with the latest tz data when needed.
 */
export function isVancouverTzOutdated (): boolean {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Vancouver',
    timeZoneName: 'shortOffset'
  })
  const parts = formatter.formatToParts(new Date('2026-11-15T12:00:00Z'))
  const timeZoneName = parts.find(p => p.type === 'timeZoneName')?.value || ''
  return /8/.test(timeZoneName) && /GMT|UTC/i.test(timeZoneName)
}

export default defineNuxtPlugin({
  name: 'polyfill-date-time-format',
  enforce: 'pre',
  async setup () {
    if (isVancouverTzOutdated()) {
      await import('@formatjs/intl-datetimeformat/polyfill-force.js')
      await import('@formatjs/intl-datetimeformat/locale-data/en.js')
      // en-CA is used for YYYY-MM-DD formatting, without it the polyfill falls back to en (MM/DD/YYYY)
      await import('@formatjs/intl-datetimeformat/locale-data/en-CA.js')
      await import('@formatjs/intl-datetimeformat/add-all-tz.js')
    }
  }
})
