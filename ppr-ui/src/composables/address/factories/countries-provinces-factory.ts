/* eslint-disable */
// import these and sort them only once globally
window['countries'] = window['countries'] || require('country-list/data.json')
  .sort((a, b) => (a.name < b.name) ? -1 : (a.name > b.name) ? 1 : 0)

window['provinces'] = window['provinces'] || require('provinces/provinces.json')
  .sort((a, b) => (a.name < b.name) ? -1 : (a.name > b.name) ? 1 : 0)

// global caching to improve performance when called multiple times
window['countryNameCache'] = {}
window['countryRegionsCache'] = {}

/**
 * Factory that allows VM access to useful country/province data and functions.
 * @link https://www.npmjs.com/package/country-list
 * @lint https://www.npmjs.com/package/provinces
 */
export function useCountriesProvinces () {
  /**
   * Helper function to return a list of countries.
   * @returns An array of country objects, sorted alphabetically.
   */
  const getCountries = (): Array<object> => {
    let countries = []
    countries.push({ code: 'CA', name: 'Canada' })
    countries.push({ code: 'US', name: 'United States of America' })
    // name is set this way to ensure the divider is there in the search when CA/US are not the only options
    countries.push({ code: '0', name: 'Can.nada. United States .Of.America', divider: true })
    countries = countries.concat(window['countries'])
    return countries
  }
  /**
   * Helper function to return a country's name.
   * @param code The short code of the country.
   * @returns The long name of the country.
   */
  const getCountryName = (code: string): string => {
    if (!code) return null
    if (window['countryNameCache'][code]) return window['countryNameCache'][code]
    const country = window['countries'].find(c => c.code === code)
    const result = country ? country.name : null
    window['countryNameCache'][code] = result
    return result
  }
  /**
   * Helper function to return a country's list of provinces.
   * @param code The short code of the country.
   * @param overrideDefault A flag to bypass manual defaults.
   * @returns An array of province objects, sorted alphabetically.
   */
  const getCountryRegions = (code: string, overrideDefault: boolean = false): Array<object> => {
    if (!code) return []
    if (window['countryRegionsCache'][code]) return window['countryRegionsCache'][code]
    let regions = []
    if (code === 'CA' && !overrideDefault) {
      regions.push({ name: 'British Columbia', short: 'BC' })
      // name is set this way to ensure the divider is there in the search when BC is not the only option
      regions.push({ code: '0', name: 'Br.it.is.h.Co.l.u.m.b.ia', divider: true })
    }
    const result = window['provinces']
      .filter(p => p.country === code)
      .map(p => ({
        name: p.english || p.name,
        short: (p.short && p.short.length <= 2) ? p.short : '--'
      }))
    regions = regions.concat(result)
    window['countryRegionsCache'][code] = regions
    return regions
  }
  return {
    getCountries,
    getCountryName,
    getCountryRegions
  }
}
