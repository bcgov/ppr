import { ref } from 'vue-demi'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './collateralFormValidator'

const createEmptyErrors = () => ({
  type: createDefaultValidationResult(),
  year: createDefaultValidationResult(),
  make: createDefaultValidationResult(),
  model: createDefaultValidationResult(),
  serialNumber: createDefaultValidationResult(),
  manufacturedHomeRegistrationNumber: createDefaultValidationResult()
})

export const useCollateralValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateInput = (fieldName, value) => {
    formValidation
      .validateField(fieldName, value)
      .then(validationResult => (errors.value[fieldName] = validationResult))
  }

  // special case, need to pass in entire record
  const validateSerial = currentVehicle => {
    formValidation
      .validateRecord(currentVehicle)
      .then(function (validationResult) {
        errors.value.serialNumber = validationResult.recordErrors.serialNumber
      })
  }

  const validateCollateralForm = async currentVehicle => {
    const validationResult = await formValidation.validateForm(currentVehicle)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    errors.value.serialNumber = validationResult.recordErrors.serialNumber

    return validationResult.succeeded
  }

  const resetSerialError = () => {
    errors.value.serialNumber = createDefaultValidationResult()
  }

  return {
    errors,
    validateInput,
    validateSerial,
    validateCollateralForm,
    resetSerialError
  }
}
