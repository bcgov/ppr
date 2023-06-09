import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeLocationIF,
  SubmittingPartyIF,
  UnitNoteIF
} from '@/interfaces'
export interface MhrRegistrationIF {
  draftNumber: string
  documentId: string
  clientReferenceId: string
  declaredValue: string
  submittingParty: SubmittingPartyIF
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  attentionReference: string
  isManualLocationInfo: boolean
  ownLand: boolean
  location: MhrRegistrationHomeLocationIF
  description: MhrRegistrationDescriptionIF
}

export interface NewMhrRegistrationApiIF {
  draftNumber?: string
  documentId: string
  clientReferenceId?: string
  declaredValue?: string
  submittingParty: {
    personName?: {
      first: string
      last: string
      middle?: string
    }
    businessName?: string
    address: {
      street: string
      city: string
      region?: string
      country?: string
      postalCode?: string
    }
    emailAddress?: string
    phoneNumber?: string
    phoneExtension?: string
  }
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  location: MhrRegistrationHomeLocationIF
  description: MhrRegistrationDescriptionIF
  attentionReference?: string
  isManualLocationInfo?: boolean
  ownLand?: boolean
  notes?: [
    {
      documentType: string
      documentId: string
      createDateTime: string
      remarks: string
      contactName: string
      contactAddress: {
        street: string
        city: string
        region: string
        postalCode: string
        country: string
      }
    }
  ]
}
