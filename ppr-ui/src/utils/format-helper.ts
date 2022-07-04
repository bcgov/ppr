/**
 * Helper function to convert string to HTML format
 * @param stringToFormat
 */
export function formatAsHtml (stringToFormat: string) {
  return stringToFormat.replace(/\r?\n/g, '<br>') // convert new line chars to html break lines
}
