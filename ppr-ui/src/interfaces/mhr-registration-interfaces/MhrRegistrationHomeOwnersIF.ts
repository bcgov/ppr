export interface MhrRegistrationHomeOwnersIF {
  individualName: {
    first: string,
    last: string
  },
  address: {
    street: string,
    city: string,
    region: string,
    country: string,
    postalCode: string
  },
  type: string
}
