
// Party Address interface.
export interface AddressIF {
  streetAddress: string, // Max length 50
  streetAddressAdditional?: string, // Max length 50
  addressCity: string, // Max length 30
  addressRegion: string, // Length 2 province/state code.
  addressCountry: string, // Length 2 couuntry code.
  postalCode: string, // Max length 15
  deliveryInstructions: string
}
