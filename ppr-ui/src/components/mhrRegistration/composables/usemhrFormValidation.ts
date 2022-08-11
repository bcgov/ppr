import { ref } from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './mhrFormValidator'
import { useValidation } from '@/utils/validators/use-validation'
const {
  validateName
} = useValidation()

const createEmptyErrors = () => ({
  phoneNumber: createDefaultValidationResult(),
  emailAddress: createDefaultValidationResult()
})

export const usemhrFormValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateInput = (fieldName, value) => {
    formValidation.validateField(fieldName, value).then(validationResult => {
      errors.value[fieldName] = validationResult
    })
  }

  /**
   * Handles validity events from address sub-components.
   * @param propertyToValidate the address to set the validity of
   * @param isValid whether the address is valid
   */
  const updateValidity = (valid: boolean): void => {
    errors.value.emailAddress.succeeded = valid
    errors.value.phoneNumber.succeeded = valid
  }

  return {
    errors,
    updateValidity,
    validateInput
  }
}
