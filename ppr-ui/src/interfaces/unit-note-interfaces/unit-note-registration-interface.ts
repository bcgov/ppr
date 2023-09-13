import { CancelUnitNoteIF, SubmittingPartyIF, UnitNoteIF } from '@/interfaces'

export interface UnitNoteRegistrationIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: SubmittingPartyIF
  note: UnitNoteIF | CancelUnitNoteIF
  cancelDocumentId?: string // document id of the note that's being cancelled
  documentType?: string // document type for staff admin registrations.
}

export interface UnitNoteStoreActionIF {
  key: string,
  value: any
}
