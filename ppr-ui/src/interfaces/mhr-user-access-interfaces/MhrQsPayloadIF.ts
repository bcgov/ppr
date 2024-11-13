import { AddressIF } from '@/interfaces'

export interface MhrQsPayloadIF {
  authorizationName: string
  businessName: string
  termsAccepted: boolean
  dbaName?: string
  address: AddressIF
  phoneNumber: string
  confirmRequirements?: boolean
}
