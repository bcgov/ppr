import { MhrRegistrationFieldValidationIF } from '@/interfaces/validation-interfaces'

export const mhrRegistrationValidation = {
  // Form fields and their respective validation rules
  fields: [
    {
      id: 'mhrRegistration.description.otherRemarks',
      validations: (fieldValue: string) => {
        // All validations would go here, returning the error for each rule
        if (fieldValue?.length > 140) {
          return 'Maximum 140 characters'
        }
      }
    }
  ] as Array<MhrRegistrationFieldValidationIF>
}
