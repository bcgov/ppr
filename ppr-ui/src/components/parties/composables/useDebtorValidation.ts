import {
  ref
} from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
// import { formValidation } from './collateralFormValidator'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  street: createDefaultValidationResult(),
  city: createDefaultValidationResult(),
  region: createDefaultValidationResult(),
  postalCode: createDefaultValidationResult()
})

export const useDebtorValidation = () => {
  const errors = ref(createEmptyErrors())

  /* const validateInput = (fieldName, value) => {
    console.log(value)
    formValidation.validateField(fieldName, value)
      .then(validationResult => (errors.value[fieldName] = validationResult))
  }

  const validateCollateralForm = async (currentVehicle) => {
    const validationResult = await formValidation.validateForm(currentVehicle)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    if (currentVehicle.type === 'MH') {
      errors.value.manufacturedHomeRegistrationNumber = validationResult.recordErrors.serialNumber
    } else {
      errors.value.serialNumber = validationResult.recordErrors.serialNumber
    }
    return validationResult.succeeded
  } */

  /**
   * Handles validity events from address sub-components.
   * @param addressToValidate the address to set the validity of
   * @param isValid whether the address is valid
   */
  const updateValidity = (isValid: boolean): void => {

  }

  return {
    errors,
    updateValidity
    // validateInput,
    // validateCollateralForm
  }
}
