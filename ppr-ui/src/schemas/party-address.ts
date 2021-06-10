import { required, maxLength } from 'vuelidate/lib/validators'

// The Party Address schema containing Vuelidate rules.
// NB: This should match the subject JSON schema.
export const PartyAddressSchema = {
  street: {
    required,
    maxLength: maxLength(50)
  },
  streetAdditional: {
    maxLength: maxLength(30)
  },
  city: {
    required,
    maxLength: maxLength(40)
  },
  country: {
    required
  },
  region: {
    maxLength: maxLength(2)
  },
  postalCode: {
    required,
    maxLength: maxLength(15)
  },
  deliveryInstructions: {
    maxLength: maxLength(80)
  }
}
