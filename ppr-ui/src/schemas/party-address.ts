import { ValidationRule } from '@/composables/address/enums'
import { baseRules, spaceRules } from '@/composables/address/factories/validation-factory'

// The Party Address schema containing Vuelidate rules.
// NB: This should match the subject JSON schema.
export const PartyAddressSchema = {
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

// The Party Address schema containing Vuelidate rules for cases where Party Address is Optional/Not Required
export const OptionalPartyAddressSchema = {
  street: [
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  streetAdditional: [
    baseRules[ValidationRule.MAX_LENGTH](50),
    ...spaceRules
  ],
  city: [
    baseRules[ValidationRule.MAX_LENGTH](40),
    ...spaceRules
  ],
  country: [
    ...spaceRules
  ],
  region: [
    ...spaceRules
  ],
  /* NOTE: Canada/US postal code and zip code regex rules
   * are added automatically as extra rules based on country
   * inside the address components
   */
  postalCode: [
  ],
  deliveryInstructions: [
    baseRules[ValidationRule.MAX_LENGTH](80),
    ...spaceRules
  ]
}
