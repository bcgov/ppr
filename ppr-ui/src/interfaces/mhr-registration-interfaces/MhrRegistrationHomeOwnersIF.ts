import { AddressIF } from "@/composables/address/interfaces"

export interface MhrRegistrationHomeOwnersIF {
  individualName: {
    first: string,
    middle: string,
    last: string
  },
  phoneNumber: number,
  phoneExtension: number
  address: AddressIF
  // type: string
}
