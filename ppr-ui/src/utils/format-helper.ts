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
