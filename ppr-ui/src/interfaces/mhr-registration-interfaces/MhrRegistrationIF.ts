import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeLocationIF,
  SubmittingPartyIF
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
  location: MhrRegistrationHomeLocationIF
  description: MhrRegistrationDescriptionIF
  notes: [
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
