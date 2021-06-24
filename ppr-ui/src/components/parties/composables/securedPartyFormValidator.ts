import { Validators, createFormValidation } from '@lemoncode/fonk'

const validationSchema = {
  field: {
    emailAddress: [Validators.email]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
