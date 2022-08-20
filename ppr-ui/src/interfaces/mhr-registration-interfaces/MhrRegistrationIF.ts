import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeOwnersIF,
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
    phoneNumber: number
    phoneExtension: number
  }
  ownerGroups: MhrRegistrationHomeOwnerGroupIF[]
  owners: MhrRegistrationHomeOwnersIF[]
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
