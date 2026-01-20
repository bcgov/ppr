/**
 * Helper function to convert string to HTML format
 * @param stringToFormat
 */
export function formatAsHtml (stringToFormat: string) {
  return stringToFormat.replace(/\r?\n/g, '<br>') // convert new line chars to html break lines
}

/**
 * Formats a phone number for display.
 * @param phoneNumber the phone number to format
 * @returns a formatted phone number
 */
export function toDisplayPhone (phoneNumber: string): string {
  // Filter only numbers from the input
  const cleaned = ('' + phoneNumber).replace(/\D/g, '')

  // Check if the input is of correct length
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)

  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3]
  } else return phoneNumber
}

/**
 * Formats a phone number for display.
 * @param phoneNumber the phone number to format
 * @returns a formatted phone number
 */
export function fromDisplayPhone (phoneNumber: string): string {
  // Filter only numbers from the input
  const cleaned = ('' + phoneNumber).replace(/\D/g, '')

  // Check if the input is of correct length
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)

  if (match) {
    return match[1] + match[2] + match[3]
  } else return phoneNumber
}

/**
 * Formats a string word to title case for display.
 * @param value the string word to format
 * @returns a title case string word
 */
export function toTitleCase (value: string): string {
  return value ? (value[0].toUpperCase() + value.slice(1).toLowerCase()) : ''
}

/**
 * Formats enum-like strings (eg, "IN_REVIEW") into a human-friendly label ("In Review").
 */
export function enumToLabel (value?: string | null): string {
  const normalized = String(value || '').replace(/_/g, ' ').trim()
  return normalized ? multipleWordsToTitleCase(normalized, false) : ''
}

/**
 * Formats a string of multiple words to title case for display.
 * @param value the string of multiple words to format
 * @param excludeWords whether to exclude certain prepositions and conjunctions
 * @returns a title case string of multiple words
 */
export function multipleWordsToTitleCase (value: string, excludeWords: boolean): string {
  // Common preopositions and conjunctions to exclude from title case (can easily add more if need be)
  const exclusions = ['or', 'to', 'of', 'with', 'under']

  const words = value?.split(' ')

  const titleCaseWords = words?.map((word, index) => {
    // If excludePrePosAndConj is true, and sentence does not start with a preposition or conjunction
    if (excludeWords && exclusions.includes(word.toLowerCase()) &&
      !(index === 0 || words[index - 1].endsWith('.'))) {
      return word.toLowerCase()
    }
    return toTitleCase(word)
  })

  return titleCaseWords?.join(' ')
}

/**
 * Formats a payment error string to extract just the rootCause message.
 * @param rootCause the string to format
 * @returns a payment error rootCause message
 */
export function parsePayDetail (rootCause: string): string {
  return rootCause?.substring(
    rootCause?.indexOf(':') + 5,
    rootCause?.indexOf('<') - 1
  )
}

/**
 * Removes any characters that are not a letter.
 * @param string the string to format
 * @returns a stripped string containing only letters
 */
export function stripChars (string: string): string {
  return string.replace(/[^A-Za-z0-9]/g, '')
}

/**
 * @function cleanEmpty
 *
 * Cleans the given object.
 * Deletes properties that has `null`, `undefined`, or `''` as values.
 *
 * @typeParam Type - type of object getting passed in
 * @param obj - The object to be cleaned up
 * @returns A new Object excluding `null`, `undefined`, or `''` values from the original Object.
 */
export function cleanEmpty<Type> (obj:Type): Type {
  const newObj = {}
  Object.keys(obj).forEach((key) => {
    if (obj[key] !== null && typeof obj[key] === 'object') { // getting deep into a nested object
      newObj[key] = cleanEmpty(obj[key])
    } else if (!!obj[key] || obj[key] === 0) { // add the key/value when it's not null, undefined, or empty string
      newObj[key] = obj[key]
    }
  })
  return newObj as Type
}

/**
 * @function removeEmptyProperties
 *
 * Cleans the given object by removing properties with `null`, `undefined`, or `''` values.
 *
 * @typeparam {Object} Type - Type of the object getting passed in.
 * @param {Object} obj - The object to be cleaned up.
 * @returns {Object} A new object excluding properties with `null`, `undefined`, or `''` values from the original object
 */
export function removeEmptyProperties(obj: object): object {
  const isNotEmpty = (value) => {
    if (value === null || value === undefined) {
      return false
    }
    if (typeof value === 'string' && value.trim() === '') {
      return false
    }
    if (Array.isArray(value) && value.length === 0) {
      return false
    }
    return !(typeof value === 'object' && Object.keys(value).length === 0);
  }

  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key) && !isNotEmpty(obj[key])) {
      delete obj[key]
    }
  }

  return obj
}

/**
 * Formats a value into a currency string with optional dollar sign and specified number of decimal places.
 *
 * @param {string | number} value - The value to be formatted. Can be a string or number.
 *                              Strings with dollar signs and commas will be converted to numbers.
 *                              For example: '1,234.56' or '$1,234.56' will both be converted to 1234.56.
 *
 * @param {number} decimal - The number of decimal places to display, default value is 2.
 *                         This sets the number of fraction digits.
 *
 * @param {boolean} dollarSign - Determines whether to include '$' in the formatted string, included by default.
 *
 * @returns {string} - Returns the formatted currency string.
 *                   If the provided value is null, undefined, or an empty string, it returns an empty string.
 *
 * @example
 * formatCurrency(1234.5678, 2, true)   // Returns '$1,234.57'
 * formatCurrency('1,234.5678', 2, false) // Returns '1,234.57'
 * formatCurrency('$1,234.5678', 3, true)  // Returns '$1,234.568'
 */
export function formatCurrency (
  value: string | number,
  decimal: number = 2,
  showDollarSign: boolean = true
): string {
  if (!value) return ''
  if (typeof value === 'string') {
    value = Number(value.replace('$', '').replace(',', ''))
  }
  const options = showDollarSign
    ? {
        style: 'currency',
        currency: 'CAD',
        minimumFractionDigits: decimal,
        maximumFractionDigits: decimal
      }
    : {
        minimumFractionDigits: decimal,
        maximumFractionDigits: decimal
      }
  return value.toLocaleString('en-CA', options)
}
