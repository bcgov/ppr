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
  submittingParty: PartyIF
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
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups: Array<MhrHomeOwnerGroupIF>
  createDateTime?: string
  deathOfOwner?: boolean
  payment?: PaymentIF
  error?: ErrorIF
  baseRegistrationNumber?: string
}

export interface MhrDraftTransferApiIF {
  type: string
  registration: MhrTransferApiIF
  error?: ErrorIF
}

export interface MhrDraftTransferResponseIF {
  createDateTime: string
  draftNumber: string
  lastUpdateDateTime: string
  registration: MhrTransferApiIF
  type: APIMhrTypes
  error?: ErrorIF
}
