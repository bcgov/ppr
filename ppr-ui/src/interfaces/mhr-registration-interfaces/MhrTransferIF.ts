import {
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationHomeOwnerGroupIF,
  PartyIF
} from '@/interfaces'

export interface MhrTransferIF {
  mhrNumber: string
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  owners: MhrRegistrationHomeOwnerIF[]
  submittingParty: PartyIF
}
