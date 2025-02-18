import type {
  MhrRegistrationHomeOwnerGroupIF,
  MhrHomeOwnerGroupIF,
  PaymentIF,
  SubmittingPartyIF,
  ErrorIF,
  TransferTypeSelectIF,
  MhrRegistrationIF
} from '@/interfaces'
import type { APIMhrTypes, ApiTRANSTransfersTypes, ApiTransferTypes } from '@/enums'

export interface MhrTransferIF {
  mhrNumber: string
  documentId?: string // required for Staff only
  transferType: TransferTypeSelectIF
  declaredValue: number
  consideration: string
  transferDate: string
  ownLand: boolean
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  currentOwnerGroups?: MhrRegistrationHomeOwnerGroupIF[]
  submittingParty: SubmittingPartyIF
  attentionReference: string
  error?: ErrorIF
  isAffidavitTransferCompleted?: boolean
}

export interface MhrTransferApiIF {
  mhrNumber: string
  documentId?: string
  documentDescription?: string
  clientReferenceId?: string
  declaredValue: number
  consideration: string
  transferDate: string
  ownLand: boolean
  registrationType: ApiTransferTypes
  transferDocumentType?: ApiTransferTypes | ApiTRANSTransfersTypes
  submittingParty: SubmittingPartyIF
  attentionReference?: string
  deleteOwnerGroups?: Array<MhrHomeOwnerGroupIF>
  addOwnerGroups: Array<MhrHomeOwnerGroupIF>
  createDateTime?: string
  payment?: PaymentIF
  error?: ErrorIF
  draftNumber?: string
}

export interface MhrDraftApiIF {
  type: string
  registration: MhrTransferApiIF | MhrRegistrationIF
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
