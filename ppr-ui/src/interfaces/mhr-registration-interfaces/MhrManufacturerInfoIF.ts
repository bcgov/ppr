import { MhrRegistrationHomeLocationIF, MhrRegistrationHomeOwnerGroupIF, SubmittingPartyIF } from '@/interfaces'

export interface MhrManufacturerInfoIF {
  authorizationName?: string
  dbaName?: string
  termsAccepted: boolean
  description: {
    manufacturer: string
  }
  location: MhrRegistrationHomeLocationIF,
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[],
  submittingParty: SubmittingPartyIF
}
