import { ValidationRule } from '@/composables/address/enums'
import { baseRules, spaceRules } from '@/composables/address/factories/validation-factory'

// The MHR Organization Home Owner schema for BaseAddress component.
export const OrganizationAddressSchema = {
  street: [
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  streetAdditional: [
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  city: [
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](40),
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
    baseRules[ValidationRule.REQUIRED]
  ],
  deliveryInstructions: [
    baseRules[ValidationRule.MAX_LENGTH](80),
    ...spaceRules
  ]
}
