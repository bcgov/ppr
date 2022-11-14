import { ref } from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './securedPartyFormValidator'
import { useValidation } from '@/utils/validators/use-validation'
import { SecuredPartyTypes } from '@/enums'
const {
  validateName
} = useValidation()

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  middle: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  emailAddress: createDefaultValidationResult(),
  address: createDefaultValidationResult()
})

export const useSecuredPartyValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateInput = (fieldName, value) => {
    formValidation.validateField(fieldName, value).then(validationResult => {
      errors.value[fieldName] = validationResult
    })
  }

  const validateSecuredPartyForm = (partyType, currentParty, isRegisteringParty): boolean => {
    const currentIsBusiness = partyType === SecuredPartyTypes.BUSINESS
    validateName(currentIsBusiness, currentParty.value, errors)
    if (isRegisteringParty) {
      if (currentParty.value.emailAddress.length === 0) {
        errors.value.emailAddress = {
          type: 'EMAIL',
          succeeded: false,
          message: 'Email address is required'
        }
      }
    }
    if (currentIsBusiness === true) {
      return (
        errors.value.businessName.succeeded &&
        errors.value.emailAddress.succeeded &&
        errors.value.address.succeeded
      )
    } else {
      return (
        errors.value.first.succeeded &&
        errors.value.middle.succeeded &&
        errors.value.last.succeeded &&
        errors.value.emailAddress.succeeded &&
        errors.value.address.succeeded
      )
    }
  }

  /**
   * Handles validity events from address sub-components.
   * @param addressToValidate the address to set the validity of
   * @param isValid whether the address is valid
   */
  const updateValidity = (valid: boolean): void => {
    errors.value.address.succeeded = valid
  }

  return {
    errors,
    updateValidity,
    validateInput,
    validateSecuredPartyForm
  }
}
