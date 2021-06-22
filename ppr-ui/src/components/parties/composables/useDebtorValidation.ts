import {
  ref
} from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './debtorFormValidator'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  year: createDefaultValidationResult(),
  month: createDefaultValidationResult(),
  day: createDefaultValidationResult(),
  street: createDefaultValidationResult(),
  city: createDefaultValidationResult(),
  region: createDefaultValidationResult(),
  postalCode: createDefaultValidationResult()
})

export const useDebtorValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateName = (isBusiness, form) => {
    if ((isBusiness) && (form.businessName.length === 0)) {
    errors.value['businessName'] = {
      type: 'NAME',
      succeeded: false,
      message: 'Please enter a business name'
    }
  }
  }

  const validateBirthdate = (form) => {
    if ((form.year > 0) || (form.month > 0) || (form.day > 0)) {
    errors.value['year'] = {
      type: 'YEAR',
      succeeded: false,
      message: 'Please enter a valid year'
    }
  }
  }

  const validateInput = (fieldName, value) => {
    console.log(value)
    formValidation.validateField(fieldName, value)
      .then(validationResult => (errors.value[fieldName] = validationResult))
  }

  const validateDebtorForm = async (currentIsBusiness, currentDebtor) => {
    const validationResult = await formValidation.validateForm(currentDebtor)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    validateBirthdate(currentDebtor)
    validateName(currentIsBusiness, currentDebtor)
    return validationResult.succeeded
  } 

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
