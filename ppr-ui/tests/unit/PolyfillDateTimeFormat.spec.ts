import { isVancouverTzOutdated } from '@/plugins/polyfill-date-time-format'

function mockTimeZoneName (tzValue: string) {
  vi.spyOn(Intl, 'DateTimeFormat').mockImplementation(function () {
    return {
      formatToParts: () => [
        { type: 'hour', value: '4' },
        { type: 'literal', value: ' ' },
        { type: 'timeZoneName', value: tzValue }
      ]
    } as unknown as Intl.DateTimeFormat
  })
}

describe('Date time format polyfill plugin', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it.each([
    ['GMT-8'],
    ['GMT-08'],
    ['GMT-08:00'],
    ['GMT−8'],
    ['GMT−08:00']
  ])('detects outdated tz data when the Nov 2026 offset is %s', (tzValue) => {
    mockTimeZoneName(tzValue)
    expect(isVancouverTzOutdated()).toBe(true)
  })

  it.each([
    ['GMT-7'],
    ['GMT-07']
  ])('does not flag tz data when the Nov 2026 offset is %s', (tzValue) => {
    mockTimeZoneName(tzValue)
    expect(isVancouverTzOutdated()).toBe(false)
  })

  it('formats America/Vancouver as UTC-7 after Nov 1, 2026 once the plugin has run', () => {
    // The plugin runs in the nuxt test environment, polyfilling if the runtime tz data is outdated
    const pacificMidnight = new Date('2026-12-16T00:00:00-07:00')
    expect(pacificMidnight.toLocaleDateString('en-CA', { timeZone: 'America/Vancouver' })).toBe('2026-12-16')
    expect(new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Vancouver',
      hour: 'numeric',
      hour12: false
    }).format(pacificMidnight)).toMatch(/^(00|24)$/)
  })
})
