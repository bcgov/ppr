
// Party Address interface.
export interface AddressIF {
  street: string, // Max length 50
  streetAdditional?: string, // Max length 50
  city: string, // Max length 30
  region: string, // Length 2 province/state code.
  country: string, // Length 2 couuntry code.
  postalCode: string, // Max length 15
  deliveryInstructions: string
}
