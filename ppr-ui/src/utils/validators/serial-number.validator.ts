export const serialNumberValidator = ({ values }) => {
  const numbersOnly = /^\d+$/
  let succeeded = true
  const minLen = 1
  const maxLen = 25
  let message = 'Maximum 25 characters'
  let emptyMessage = ''
  let valueToValidate = values.serialNumber?.trim()

  if (
    values.type === 'MH' &&
    values.manufacturedHomeRegistrationNumber &&
    values.manufacturedHomeRegistrationNumber.length > 0
  ) {
    valueToValidate = values.manufacturedHomeRegistrationNumber.trim()
  }

  switch (values.type) {
    case 'AC':
      message = 'Maximum 25 characters'
      emptyMessage = 'Enter the D.O.T. Number'
      break
    case 'AF':
      emptyMessage = 'Enter the D.O.T. or Serial Number'
      break
    case 'MH':
      emptyMessage =
        'Either the Manufactured Home Registration Number or Serial Number is required'
      message =
        'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
      break
    case 'MV':
      emptyMessage = 'Enter the Serial or VIN Number'
      message =
        'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
      break
    case 'OB':
    case 'TR':
    case 'BO':
      emptyMessage = 'Enter the Serial Number'
      message =
        'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
      break
  }

  if (valueToValidate.length === 0) {
    message = emptyMessage
  }

  if (valueToValidate.length < minLen) {
    succeeded = false
  }
  if (valueToValidate.length > maxLen) {
    succeeded = false
  }
  return {
    succeeded,
    message: succeeded ? '' : message,
    type: 'SERIAL_NUMBER'
  }
}
