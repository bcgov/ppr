import { Validators, createFormValidation } from '@lemoncode/fonk'
import { rangeNumber } from '@lemoncode/fonk-range-number-validator'
import { serialNumberValidator } from '@/utils/validators/serial-number.validator'

const validationSchema = {
  field: {
    type: [
      {
        validator: Validators.required.validator,
        message: 'Type is required',
        customArgs: { trim: true }
      }
    ],
    model: [
      {
        validator: Validators.required.validator,
        message: 'Enter the vehicle model',
        customArgs: { trim: true }
      },
      {
        validator: Validators.maxLength.validator,
        customArgs: { length: 60 },
        message: 'Maximum {{length}} characters'
      }
    ],
    manufacturedHomeRegistrationNumber: [
      {
        validator: Validators.pattern,
        customArgs: { pattern: /^\d{6}$/ },
        message: 'Manufactured Home Registration Number must contain 6 digits'
      }
    ],
    year: [
      {
        validator: rangeNumber.validator,
        customArgs: {
          strictTypes: false,
          min: {
            value: 1800,
            inclusive: true
          },
          max: {
            value: new Date().getFullYear() + 1,
            inclusive: true
          }
        },
        message: 'Enter a valid year'
      }
    ],
    make: [
      {
        validator: Validators.required.validator,
        message: 'Enter the vehicle make',
        customArgs: { trim: true }
      },
      {
        validator: Validators.maxLength.validator,
        customArgs: { length: 60 },
        message: 'Maximum {{length}} characters'
      }
    ]
  },
  record: {
    serialNumber: [
      {
        validator: serialNumberValidator
      }
    ]
  }
}
// @ts-ignore - there is a type mismatch in the structure above, but it still works
export const formValidation = createFormValidation(validationSchema)
