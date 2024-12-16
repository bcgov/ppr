import { ValidationRule } from '@/composables/address/enums'
import { baseRules, spaceRules } from '@/composables/address/factories/validation-factory'

// The Civic Address schema containing Vuelidate rules.
// NB: This should match the subject JSON schema.
export const CivicAddressSchema = {
  street: [
    baseRules[ValidationRule.MAX_LENGTH](31),
    ...spaceRules
  ],
  streetAdditional: [
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  city: [
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](20),
    ...spaceRules
  ],
  country: [
    baseRules[ValidationRule.REQUIRED],
    ...spaceRules
  ],
  region: [
    baseRules[ValidationRule.REQUIRED],
    ...spaceRules
  ],
  /* NOTE: Canada/US postal code and zip code regex rules
   * are added automatically as extra rules based on country
   * inside the address components
   */
  postalCode: [
  ],
  deliveryInstructions: [
  ]
}

export const ManufacturerCivicAddressSchema = {
  street: [
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](31),
    ...spaceRules
  ],
  streetAdditional: [
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  city: [
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](20),
    ...spaceRules
  ],
  country: [
    baseRules[ValidationRule.REQUIRED],
    ...spaceRules
  ],
  region: [
    baseRules[ValidationRule.REQUIRED],
    ...spaceRules
  ],
  /* NOTE: Canada/US postal code and zip code regex rules
   * are added automatically as extra rules based on country
   * inside the address components
   */
  postalCode: [
  ],
  deliveryInstructions: [
  ]
}
