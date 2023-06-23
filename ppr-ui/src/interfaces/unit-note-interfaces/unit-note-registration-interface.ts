import { AddressIF, UnitNoteIF } from '@/interfaces'

export interface UnitNoteRegistrationIF {
  clientReferenceId: string
  attentionReference: string
  submittingParty: {
    businessName: string
    address: AddressIF
    phoneNumber: string
    emailAddress: string
  }
  note: UnitNoteIF
}

export interface UnitNoteStoreActionIF {
  key: string,
  value: any
}
