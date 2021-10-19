import { Validators, createFormValidation } from '@lemoncode/fonk'

const validationSchema = {
  field: {
    courtName: [
      {
        validator: Validators.required.validator,
        message: 'Enter the court name',
        customArgs: { trim: true }
      }
    ],
    courtRegistry: [
      {
        validator: Validators.required.validator,
        message: 'Enter the court registry',
        customArgs: { trim: true }
      }
    ],
    fileNumber: [
      {
        validator: Validators.required.validator,
        message: 'Enter the court file number',
        customArgs: { trim: true }
      }
    ],
    orderDate: [
      {
        validator: Validators.required.validator,
        message: 'Select the date of the order',
        customArgs: { trim: true }
      }
    ],
    effectOfOrder: [
      {
        validator: Validators.required.validator,
        message: 'Enter the effect of order',
        customArgs: { trim: true }
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
