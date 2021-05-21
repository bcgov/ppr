export const serialNumberValidator = ({ values }) => {
  const numbersOnly = /^\d+$/
  let succeeded = true
  let minLen = 1
  let maxLen = 25
  let message = 'Maximum 25 letters'
  if (values.type === 'MH') {
    if (!numbersOnly.test(values.serialNumber)) {
      succeeded = false
    }
    message = 'Manufactured home registration number must contain 6 digits'
  }
  if (values.type === 'BO') {
    minLen = 6
    maxLen = 6
  }
  if (values.serialNumber.length < minLen) {
    succeeded = false
  }
  if (values.serialNumber.length > maxLen) {
    succeeded = false
  }
  return {
    succeeded,
    message: succeeded ? '' : message,
    type: 'SERIAL_NUMBER'
  }
}
