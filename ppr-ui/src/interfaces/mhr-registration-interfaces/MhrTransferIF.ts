import {
  MhrRegistrationHomeOwnersIF,
  MhrRegistrationHomeOwnerGroupIF,
  PartyIF
} from '@/interfaces'

export interface MhrTransferIF {
  mhrNumber: string
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  owners: MhrRegistrationHomeOwnersIF[]
  submittingParty: PartyIF
}
