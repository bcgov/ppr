export const serialNumberValidator = ({ values }) => {
  const numbersOnly = /^\d+$/
  let succeeded = true
  let minLen = 1
  let maxLen = 25
  let message = 'Maximum 25 letters'
  let emptyMessage = ''
  let valueToValidate = values.serialNumber

  if ((values.type === 'MH') && (values.manufacturedHomeRegistrationNumber.length > 0)) {
    valueToValidate = values.manufacturedHomeRegistrationNumber
  }

  switch (values.type) {
    case 'AC':
      emptyMessage = 'Enter the Aircraft Airframe D.O.T Number'
      break
    case 'AF':
      emptyMessage = 'Enter the Aircraft Airframe D.O.T Number'
      break
    case 'BO':
      emptyMessage = 'Enter the Boat Serial Number'
      break
    case 'MH':
      if (!numbersOnly.test(valueToValidate)) {
        succeeded = false
      }
      minLen = 6
      maxLen = 6
      emptyMessage = 'Enter the Manufactured Home Registration Number'
      message = 'Manufactured home registration number must contain 6 digits'
      break
    case 'MV':
      emptyMessage = 'Enter the Serial / VIN Number'
      break
    case 'OM':
      emptyMessage = 'Enter the Outboard Motor Serial Number'
      break
    case 'TR':
      emptyMessage = 'Enter the Trailer Serial Number'
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
