import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import { AddressIF, SubmittingPartyIF } from '..'

export interface MhrRegistrationUnitNoteIF {
  documentType: UnitNoteDocTypes
  documentId: string
  documentRegistrationNumber: string
  documentDescription: string
  createDateTime: string
  effectiveDateTime: string
  expiryDateTime: string
  status: UnitNoteStatusTypes
  remarks: string
  givingNoticeParty: SubmittingPartyIF
  destroyed: boolean
}

export interface MhrUnitNoteIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: {
    businessName: string
    address: AddressIF
    phoneNumber: string
    emailAddress: string
  }
  note: MhrRegistrationUnitNoteIF
}
