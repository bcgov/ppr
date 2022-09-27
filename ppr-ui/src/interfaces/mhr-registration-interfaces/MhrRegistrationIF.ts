import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeLocationIF
} from '@/interfaces'
export interface MhrRegistrationIF {
  documentId: string
  clientReferenceId: string
  declaredValue: string
  submittingParty: {
    personName: {
      first: string
      last: string
      middle: string
    }
    businessName: string
    address: {
      street: string
      city: string
      region: string
      country: string
      postalCode: string
    }
    emailAddress: string
    phoneNumber: string
    phoneExtension: string
  }
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  attentionReferenceNum: string
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
  attentionReferenceNum?: string
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
