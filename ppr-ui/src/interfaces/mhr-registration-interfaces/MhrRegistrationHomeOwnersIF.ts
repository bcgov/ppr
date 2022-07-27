import { AddressIF } from '@/composables/address/interfaces'

export interface MhrRegistrationHomeOwnersIF {
  id?: string, // optional property used for editing a home owner
  individualName?: {
    first: string,
    middle: string,
    last: string
  },
  suffix?: string,
  organizationName?: string,
  phoneNumber: string,
  phoneExtension: number
  address: AddressIF
  // type: string
}
