import {
  ref
} from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './securedPartyFormValidator'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  emailAddress: createDefaultValidationResult(),
  street: createDefaultValidationResult(),
  city: createDefaultValidationResult(),
  region: createDefaultValidationResult(),
  postalCode: createDefaultValidationResult()
})

export const useSecuredPartyValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateName = (isBusiness, form) => {
    if (isBusiness === true) {
      if (form.businessName.length === 0) {
        errors.value.businessName = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a business name'
        }
      } else {
        resetError('businessName')
      }
    } else {
      if (form.personName.first.length === 0) {
        errors.value.first = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a first name'
        }
      } else {
        resetError('first')
      }
      if (form.personName.last.length === 0) {
        errors.value.last = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a last name'
        }
      } else {
        resetError('last')
      }
    }
  }

  const validateSecuredPartyForm = (
    currentIsBusiness,
    currentDebtor
  ): boolean => {
   
    validateName(currentIsBusiness.value, currentDebtor.value)
    if (currentIsBusiness.value === true) {
      return errors.value.businessName.succeeded
    } else {
      return (
        errors.value.first.succeeded &&
        errors.value.last.succeeded &&
        errors.value.emailAddress.succeeded
      )
    }
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
