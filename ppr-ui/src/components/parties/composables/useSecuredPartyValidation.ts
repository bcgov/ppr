import { ref } from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './securedPartyFormValidator'
import { useValidation } from '@/utils/validators/use-validation'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  emailAddress: createDefaultValidationResult(),
  address: createDefaultValidationResult()
})

export const useSecuredPartyValidation = () => {
  const errors = ref(createEmptyErrors())
  const { resetError } = useValidation()

  const validateInput = (fieldName, value) => {
    formValidation.validateField(fieldName, value).then(validationResult => {
      errors.value[fieldName] = validationResult
    })
  }

  const validateName = (isBusiness, form) => {
    if (form.businessName) {
      form.businessName = form.businessName.trim()
    }
    if (form.personName) {
      form.personName.first = form.personName.first.trim()
      form.personName.last = form.personName.last.trim()
    }
    if (isBusiness === true) {
      if (form.businessName.length === 0) {
        errors.value.businessName = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a business name'
        }
      } else {
        errors.value = resetError('businessName', errors.value)
      }
    } else {
      if (form.personName.first.length === 0) {
        errors.value.first = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a first name'
        }
      } else {
        errors.value = resetError('first', errors.value)
      }
      if (form.personName.last.length === 0) {
        errors.value.last = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a last name'
        }
      } else {
        errors.value = resetError('last', errors.value)
      }
    }
  }

  const validateSecuredPartyForm = (partyBusiness, currentParty, isRegisteringParty): boolean => {
    const currentIsBusiness = partyBusiness === 'B'
    validateName(currentIsBusiness, currentParty.value)
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
