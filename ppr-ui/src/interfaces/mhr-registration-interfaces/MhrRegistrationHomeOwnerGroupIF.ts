import { MhrRegistrationHomeOwnerIF } from './MhrRegistrationHomeOwnerIF'

export interface MhrRegistrationHomeOwnerGroupIF {
  groupId: string
  owners: MhrRegistrationHomeOwnerIF[]
  type?: string
  interest?: string
  interestNumerator?: number
  tenancySpecified?: Boolean
}
