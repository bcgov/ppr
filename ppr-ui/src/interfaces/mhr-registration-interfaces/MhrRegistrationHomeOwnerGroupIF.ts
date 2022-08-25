import { MhrRegistrationHomeOwnersIF } from './MhrRegistrationHomeOwnersIF'
import { MhrRegistrationFractionalOwnershipIF } from './MhrRegistrationFractionalOwnershipIF'
export interface MhrRegistrationHomeOwnerGroupIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: string,
  owners: MhrRegistrationHomeOwnersIF[],
  type: string // type is required for MHR submission
}
