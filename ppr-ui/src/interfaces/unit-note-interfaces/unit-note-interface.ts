import { MhApiStatusTypes, UnitNoteDocTypes } from '@/enums'
import { PartyIF } from '@/interfaces'

export interface UnitNoteIF {
  documentType: UnitNoteDocTypes
  documentId?: string
  documentRegistrationNumber?: string
  documentDescription?: string
  createDateTime?: string
  effectiveDateTime?: string
  expiryDateTime?: string
  remarks?: string
  givingNoticeParty: PartyIF
  status?: MhApiStatusTypes
  destroyed?: boolean
}
