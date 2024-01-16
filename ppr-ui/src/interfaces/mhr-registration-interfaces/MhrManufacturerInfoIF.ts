import { MhrRegistrationHomeLocationIF, MhrRegistrationHomeOwnerGroupIF, SubmittingPartyIF } from '@/interfaces'

export interface MhrManufacturerInfoIF {
  authorizationName?: string
  dbaName?: string
  description: {
    manufacturer: string
  }
  location: MhrRegistrationHomeLocationIF,
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[],
  submittingParty: SubmittingPartyIF
}
