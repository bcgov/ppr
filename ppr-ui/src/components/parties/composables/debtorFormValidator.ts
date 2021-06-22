import { Validators, createFormValidation } from '@lemoncode/fonk'
import { rangeNumber } from '@lemoncode/fonk-range-number-validator'
import { individualBusinessNameValidator } from '@/utils/validators/individual-business-name.validator'

const validationSchema = {
  field: {
    email: [
      {
        validator: Validators.email.validator,
        message: 'Please enter a valid email address'
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
