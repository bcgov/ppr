import type { MhrRegistrationHomeOwnerIF, MhrRegistrationFractionalOwnershipIF } from '@/interfaces'
import type { ActionTypes } from '@/enums'

export interface MhrRegistrationHomeOwnerGroupIF extends MhrRegistrationFractionalOwnershipIF {
  groupId: number,
  owners: MhrRegistrationHomeOwnerIF[],
  type: string // type is required for MHR submission
  action?: ActionTypes
}
export interface MhrHomeOwnerGroupIF extends MhrRegistrationHomeOwnerGroupIF {}
