import { Validators, createFormValidation } from '@lemoncode/fonk'

const validationSchema = {
  field: {
    courtName: [
      {
        validator: Validators.required.validator,
        message: 'Court name is required',
        customArgs: { trim: true }
      }
    ],
    courtRegistry: [
      {
        validator: Validators.required.validator,
        message: 'Registry is required',
        customArgs: { trim: true }
      }
    ],
    fileNumber: [
      {
        validator: Validators.required.validator,
        message: 'File number is required',
        customArgs: { trim: true }
      }
    ],
    orderDate: [
      {
        validator: Validators.required.validator,
        message: 'Date of order is required',
        customArgs: { trim: true }
      }
    ],
    effectOfOrder: [
      {
        validator: Validators.required.validator,
        message: 'Effect of order is required',
        customArgs: { trim: true }
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
