import { MhrRegistrationHomeLocationIF, MhrRegistrationHomeOwnerGroupIF, SubmittingPartyIF } from '@/interfaces'

export interface MhrManufacturerInfoIF {
  description: {
    manufacturer: string
  }
  location: MhrRegistrationHomeLocationIF,
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[],
  submittingParty: SubmittingPartyIF
}
