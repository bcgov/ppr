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
  return (value[0]?.toUpperCase() + value.slice(1)?.toLowerCase()) || ''
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
