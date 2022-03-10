import { Validators, createFormValidation } from '@lemoncode/fonk'

const validationSchema = {
  field: {
    courtName: [
      {
        validator: Validators.required.validator,
        message: 'This field is required',
        customArgs: { trim: true }
      },
      {
        validator: Validators.minLength.validator,
        message: 'Minimum 5 characters',
        customArgs: { length: 5 }
      },
      {
        validator: Validators.maxLength.validator,
        message: 'Maximum 256 characters',
        customArgs: { length: 256 }
      }
    ],
    courtRegistry: [
      {
        validator: Validators.required.validator,
        message: 'This field is required',
        customArgs: { trim: true }
      },
      {
        validator: Validators.minLength.validator,
        message: 'Minimum 5 characters',
        customArgs: { length: 5 }
      },
      {
        validator: Validators.maxLength.validator,
        message: 'Maximum 64 characters',
        customArgs: { length: 64 }
      }
    ],
    fileNumber: [
      {
        validator: Validators.required.validator,
        message: 'This field is required',
        customArgs: { trim: true }
      },
      {
        validator: Validators.minLength.validator,
        message: 'Minimum 5 characters',
        customArgs: { length: 5 }
      },
      {
        validator: Validators.maxLength.validator,
        message: 'Maximum 20 characters',
        customArgs: { length: 20 }
      }
    ],
    orderDate: [
      {
        validator: Validators.required.validator,
        message: 'This field is required',
        customArgs: { trim: true }
      }
    ],
    effectOfOrder: [
      {
        validator: Validators.required.validator,
        message: 'This field is required',
        customArgs: { trim: true }
      },
      {
        validator: Validators.minLength.validator,
        message: 'Minimum 5 characters',
        customArgs: { length: 5 }
      },
      {
        validator: Validators.maxLength.validator,
        message: 'Maximum 512 characters',
        customArgs: { length: 512 }
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
