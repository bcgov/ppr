import { required, maxLength } from 'vuelidate/lib/validators'

// The Party Address schema containing Vuelidate rules.
// NB: This should match the subject JSON schema.
export const PartyAddressSchema = {
  streetAddress: {
    // required,
    // maxLength: maxLength(50)
  },
  streetAddressAdditional: {
    // maxLength: maxLength(30)
  },
  addressCity: {
    // required,
    // maxLength: maxLength(40)
  },
  addressCountry: {
    // required
  },
  addressRegion: {
    // maxLength: maxLength(2)
  },
  postalCode: {
    // required,
    // maxLength: maxLength(15)
  },
  deliveryInstructions: {
    // maxLength: maxLength(80)
  }
}
