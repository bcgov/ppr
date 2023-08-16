import { AddressIF } from '@/interfaces'

export interface MhrQsPayloadIF {
  authorizationName: string
  businessName: string
  dbaName: string
  address: AddressIF
  phoneNumber: number
}
