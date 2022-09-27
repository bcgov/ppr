import {
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationHomeOwnerGroupIF,
  PartyIF, MhrHomeOwnerGroupIF, PaymentIF, SubmittingPartyIF
} from '@/interfaces'

export interface MhrTransferIF {
  mhrNumber: string
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  submittingParty: PartyIF
}

export interface MhrTransferApiIF {
  mhrNumber: string
  documentId?: number
  documentDescription?: string
  clientReferenceId?: string
  submittingParty: SubmittingPartyIF
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups: Array<MhrHomeOwnerGroupIF>
  createDateTime?: string
  deathOfOwner?: boolean
  payment?: PaymentIF
}
