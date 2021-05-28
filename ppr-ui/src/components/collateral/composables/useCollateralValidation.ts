import {
  ref,
  computed,
  defineComponent,
  reactive,
  toRefs,
  onMounted
} from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { formValidation } from './collateralFormValidator'

const createEmptyErrors = () => ({
  type: createDefaultValidationResult(),
  year: createDefaultValidationResult(),
  make: createDefaultValidationResult(),
  model: createDefaultValidationResult(),
  serialNumber: createDefaultValidationResult()
})

export const useCollateralValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateInput = (fieldName, value) => {
    console.log(value)
    formValidation.validateField(fieldName, value)
      .then(validationResult => (errors.value[fieldName] = validationResult))
  }

  const validateCollateralForm = async (currentVehicle) => {
    const validationResult = await formValidation.validateForm(currentVehicle)
    errors.value = { ...errors.value, ...validationResult.fieldErrors }
    errors.value.serialNumber = validationResult.recordErrors.serialNumber

    return validationResult.succeeded
  }

  return {
    errors,
    validateInput,
    validateCollateralForm
  }
}
