import { CancelUnitNoteIF, SubmittingPartyIF, UnitNoteIF } from '@/interfaces'

export interface UnitNoteRegistrationIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: SubmittingPartyIF
  note: UnitNoteIF | CancelUnitNoteIF
}

export interface UnitNoteStoreActionIF {
  key: string,
  value: any
}
