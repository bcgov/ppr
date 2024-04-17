import { PartyIF } from '@/interfaces'
import { NonResConvertedReasons, NonResDestroyedReasons, UnitNoteDocTypes } from '@/enums'

export interface ExemptionIF {
  documentId: string
  clientReferenceId: string
  attentionReference: string
  submittingParty: PartyIF
  nonResidential: boolean
  note: {
    documentType: UnitNoteDocTypes
    remarks: string
    destroyed?: boolean
    nonResidentialReason?: NonResDestroyedReasons|NonResConvertedReasons
    nonResidentialOther?: string
  }
}

export interface ExemptionValidationIF {
  documentId: boolean
  remarks: boolean
  submittingParty: boolean
  attention: boolean
  folio: boolean
  confirmCompletion: boolean
  authorization: boolean
  staffPayment: boolean
}
