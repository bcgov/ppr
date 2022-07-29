import { AddressIF } from '@/composables/address/interfaces'
import { MhrRegistrationHomeOwnersIF } from './MhrRegistrationHomeOwnersIF'

export interface MhrRegistrationHomeOwnerGroupIF {
  groupId: string,
  owners: MhrRegistrationHomeOwnersIF[],
  type?: string,
  interest?: string,
  interestNumerator?: number,
  tenancySpecified?: Boolean
}
