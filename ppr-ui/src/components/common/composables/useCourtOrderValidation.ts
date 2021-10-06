import {
  ref
} from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './courtOrderFormValidator'

const createEmptyErrors = () => ({
  courtName: createDefaultValidationResult(),
  courtRegistry: createDefaultValidationResult(),
  fileNumber: createDefaultValidationResult(),
  orderDate: createDefaultValidationResult(),
  effectOfOrder: createDefaultValidationResult()
})

export const useCourtOrderValidation = () => {
  const errors = ref(createEmptyErrors())

  /* show the errors */
  const validateCourtOrderForm = async courtOrder => {
    const validationResult = await formValidation.validateForm(courtOrder)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    return validationResult.succeeded
  }

  /* only return whether valid */
  const isValidCourtOrderForm = async courtOrder => {
    const validationResult = await formValidation.validateForm(courtOrder)
    return validationResult.succeeded
  }

  return {
    errors,
    isValidCourtOrderForm,
    validateCourtOrderForm
  }
}
