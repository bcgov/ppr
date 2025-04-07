import type { PartyIF } from '@/interfaces'
import type { NonResConvertedReasons, NonResDestroyedReasons, NonResOptions, UnitNoteDocTypes } from '@/enums'

export interface ExemptionIF {
  documentId: string
  clientReferenceId: string
  attentionReference: string
  submittingParty: PartyIF
  nonResidential: boolean
  note: ExemptionNoteIF
}

export interface ExemptionNoteIF {
  documentType: UnitNoteDocTypes
  remarks: string
  destroyed?: boolean
  nonResidentialOption?: NonResOptions // Also used to determine DESTROYED at point of submission
  nonResidentialReason?: NonResDestroyedReasons|NonResConvertedReasons
  nonResidentialOther?: string
  expiryDateTime?: string // (date-time)
}

export interface ExemptionValidationIF {
  documentId: boolean
  declarationDetails: boolean
  remarks: boolean
  submittingParty: boolean
  attention: boolean
  folio: boolean
  confirmCompletion: boolean
  authorization: boolean
  staffPayment: boolean
}
