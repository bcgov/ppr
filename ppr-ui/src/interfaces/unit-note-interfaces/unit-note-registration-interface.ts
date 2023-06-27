import { SubmittingPartyIF, UnitNoteIF } from '@/interfaces'

export interface UnitNoteRegistrationIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: SubmittingPartyIF
  note: UnitNoteIF
}

export interface UnitNoteStoreActionIF {
  key: string,
  value: any
}
