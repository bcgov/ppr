import {
  ref
} from 'vue-demi'
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
  const valid = ref(false)

  /* show the errors */
  const validateCourtOrderForm = async courtOrder => {
    const validationResult = await formValidation.validateForm(courtOrder)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    valid.value = validationResult.succeeded
  }

  /* only return whether valid */
  const isValidCourtOrderForm = async courtOrder => {
    const validationResult = await formValidation.validateForm(courtOrder)
    valid.value = validationResult.succeeded
  }

  const resetErrors = () => {
    errors.value = { ...createEmptyErrors() }
    valid.value = true
  }

  return {
    errors,
    valid,
    isValidCourtOrderForm,
    resetErrors,
    validateCourtOrderForm
  }
}
