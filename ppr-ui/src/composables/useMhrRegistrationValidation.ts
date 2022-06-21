import { mhrRegistrationValidation } from '@/utils/validators'
import { get, find } from 'lodash'

/**
 * A composable for handing field validation and error messages retrieval
 */

export const useMhrRegistrationValidation = (state, fieldId) => {
  // Find validation rules for specific field id
  const fieldValidations = find(mhrRegistrationValidation.fields, {
    id: fieldId
  })

  // Get value of the field from the model
  const filedValue = get(state, fieldId)

  // Validate value and return an error message
  return fieldValidations.validations(filedValue)
}
