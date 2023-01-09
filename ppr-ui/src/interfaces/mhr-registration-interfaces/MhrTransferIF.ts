import {
  MhrRegistrationHomeOwnerGroupIF,
  PartyIF,
  MhrHomeOwnerGroupIF,
  PaymentIF,
  SubmittingPartyIF, ErrorIF
} from '@/interfaces'
import { APIMhrTypes } from '@/enums'

export interface MhrTransferIF {
  mhrNumber: string
  declaredValue: number
  consideration: string
  transferDate: string
  ownLand: boolean
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  currentOwnerGroups?: MhrRegistrationHomeOwnerGroupIF[]
  submittingParty: SubmittingPartyIF
  attentionReference: string
  error?: ErrorIF
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
  attentionReference: string
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups: Array<MhrHomeOwnerGroupIF>
  createDateTime?: string
  deathOfOwner?: boolean
  payment?: PaymentIF
  error?: ErrorIF
  draftNumber?: string
}

export interface MhrDraftTransferApiIF {
  type: string
  registration: MhrTransferApiIF
  error?: ErrorIF
  baseRegistrationNumber?: string
}

export interface MhrDraftTransferResponseIF {
  createDateTime: string
  draftNumber: string
  lastUpdateDateTime: string
  registration: MhrTransferApiIF
  type: APIMhrTypes
  error?: ErrorIF
}
