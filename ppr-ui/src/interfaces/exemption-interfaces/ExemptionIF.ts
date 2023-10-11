import { PartyIF } from '@/interfaces'
import { UnitNoteDocTypes } from '@/enums'

export interface ExemptionIF {
  documentId: string
  clientReferenceId: string
  attentionReference: string
  submittingParty: PartyIF
  nonResidential: boolean
  note: {
    documentType: UnitNoteDocTypes
    remarks: string
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
