import { Validators, createFormValidation } from '@lemoncode/fonk'

const validationSchema = {
  field: {
    emailAddress: [
      {
        validator: Validators.email.validator,
        message: 'Please enter a valid email address'
      }
    ],
    phoneNumber: [
      {
        validator: Validators.minLength.validator,
        customArgs: { length: 14 },
        message: 'Length must be 10 numbers eg. (999) 999-9999'
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
