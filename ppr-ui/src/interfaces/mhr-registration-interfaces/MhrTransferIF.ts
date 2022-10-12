import {
  MhrRegistrationHomeOwnerGroupIF,
  PartyIF,
  MhrHomeOwnerGroupIF,
  PaymentIF,
  SubmittingPartyIF
} from '@/interfaces'

export interface MhrTransferIF {
  mhrNumber: string
  declaredValue: number
  consideration: string
  transferDate: string
  ownLand: boolean
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  currentOwnerGroups?: MhrRegistrationHomeOwnerGroupIF[]
  submittingParty: PartyIF
}

export interface MhrTransferApiIF {
  mhrNumber: string
  documentId?: number
  documentDescription?: string
  clientReferenceId?: string
  declaredValue: number
  consideration: string
  transferDate: string
  ownLand: boolean
  submittingParty: SubmittingPartyIF
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups: Array<MhrHomeOwnerGroupIF>
  createDateTime?: string
  deathOfOwner?: boolean
  payment?: PaymentIF
}
