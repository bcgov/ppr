import { PartyIF } from '@/interfaces'
import { UnitNoteDocTypes } from '@/enums'

export interface ExemptionIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: PartyIF,
  nonResidential: boolean
  note: {
    documentType: UnitNoteDocTypes
    remarks: string
  }
}
