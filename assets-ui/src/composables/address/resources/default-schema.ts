import { ValidationRule } from '@/composables/address/enums'
import { SchemaIF } from '@/composables/address/interfaces'
import { baseRules, spaceRules } from '@/composables/address/factories/validation-factory'

/* example of what to pass in for the schema */
export const DefaultSchema: SchemaIF = {
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
    baseRules[ValidationRule.REQUIRED],
    baseRules[ValidationRule.MAX_LENGTH](15),
    ...spaceRules
  ],
  deliveryInstructions: [
    baseRules[ValidationRule.MAX_LENGTH](80),
    ...spaceRules
  ]
}
