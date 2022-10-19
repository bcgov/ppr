import { MhrRegistrationHomeOwnerIF } from './MhrRegistrationHomeOwnerIF'
import { MhrRegistrationFractionalOwnershipIF } from './MhrRegistrationFractionalOwnershipIF'
export interface MhrRegistrationHomeOwnerGroupIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number,
  owners: MhrRegistrationHomeOwnerIF[],
  type: string // type is required for MHR submission
}
export interface MhrHomeOwnerGroupIF extends MhrRegistrationHomeOwnerGroupIF {}
