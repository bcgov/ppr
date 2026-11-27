import type { BaseDataUnionIF } from '@/interfaces'
import { isEqualWith } from 'lodash'

export function isSigningIn (): boolean {
  const path = window.location.pathname
  return path.includes('/login') || path.includes('/signin')
}

export function isSigningOut (): boolean {
  const path = window.location.pathname
  return path.includes('/signout')
}

/**
 * Checks if an object or its nested objects
 * have a non-object property with a truthy value
 */
export function hasTruthyValue (obj: object) {
  return obj && Object.values(obj).some(
    (value) => !!value && (typeof value === 'object' ? hasTruthyValue(value) : true)
  )
}

/** Returns the key of specified value */
export function getKeyByValue (obj, value) {
  return Object.keys(obj)?.find(key => obj[key] === value) || null
}

/** Scrolls to top of current window **/
export const scrollToTop = () => {
  const scrollDuration = 600 // Adjust the duration of the scroll animation (in milliseconds)
  const scrollStep = -window.scrollY / (scrollDuration / 15)

  const scrollInterval = setInterval(() => {
    if (window?.scrollY !== 0) {
      window?.scrollBy(0, scrollStep);
    } else {
      clearInterval(scrollInterval);
    }
  }, 15)
}

/**
 * Basic filtering function
 * @param list The list to filter
 * @param filterBy The value to filter duplicates of
 * **/
export const filterDuplicates = (list: Array<any>, filterBy: string) => {
  const uniqueCodes = new Set()
  return list.filter(item => {
    if (!uniqueCodes.has(item[filterBy])) {
      uniqueCodes.add(item[filterBy])
      return true
    }
    return false
  })
}

/** Helper function to remove properties with undefined/null/empty values **/
const removeEmptyProperties = (obj: any) => {
  for (const key in obj) {
    if (obj[key] === undefined || obj[key] === null || obj[key] === '') {
      delete obj[key]
    } else if (typeof obj[key] === 'object') {
      removeEmptyProperties(obj[key])
    }
  }
}

/** Insensitive string comparison helper. */
export const insensitiveStrCompare = (v1, v2) => !v1?.localeCompare(v2, undefined, { sensitivity: 'accent' })

/**
 * Deeply compares two values, supporting objects, arrays, and case-insensitive string comparison.
 *
 * @param base - The first value to compare.
 * @param current - The second value to compare.
 * @param isCaseSensitive - Flag for case-sensitive string comparison. Defaults to false.
 * @param cleanEmptyProperties - Clean emppty/null/undefined properties from comparisons: true by default.
 * @returns {boolean} - Returns true if the values are different, false if they are equal.
 */
export const deepChangesComparison = (
  base: BaseDataUnionIF,
  current: BaseDataUnionIF,
  isCaseSensitive: boolean = false,
  cleanEmptyProperties: boolean = true
): boolean => {

  // Remove undefined properties before comparison
  if (cleanEmptyProperties) {
    removeEmptyProperties(base)
    removeEmptyProperties(current)
  }

  // Return booleans
  if(typeof current === 'boolean') {
    return base !== current
  }

  // Return deep comparison with case options when at least one property is defined
  return (!!base || !!current) && !isEqualWith(base, current,
    (v1, v2) => (typeof v1 === 'string' && !isCaseSensitive) ? insensitiveStrCompare(v1, v2) : undefined
  )
}

/** Removes invisible Unicode whitespace and trims the name. */
export const sanitizeName = (name: string): string =>
  name.replace(/[\u00A0-\u00BF\u2000-\u200F\u2028-\u202F\uFEFF]/g, '').trim()
