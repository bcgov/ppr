import { AddressIF } from '@/composables/address/interfaces'

export interface MhrRegistrationHomeOwnerIF {
  id?: string, // optional property used for editing a home owner
  groupId?: string,
  individualName?: {
    first: string,
    middle: string,
    last: string
  },
  suffix?: string,
  organizationName?: string,
  phoneNumber: string,
  phoneExtension: string,
  address: AddressIF
  // type: string
}
