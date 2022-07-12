import { MhrRegistrationDescriptionIF, MhrRegistrationHomeOwnersIF } from '@/interfaces'

export interface MhrRegistrationIF {
  clientReferenceId: string,
  declaredValue: string,
  submittingParty: {
    businessName: string,
    address: {
      street: string,
      city: string,
      region: string,
      country: string,
      postalCode: string
    },
    emailAddress: string,
    phoneNumber: number,
    phoneExtension: number
  },
  owners: MhrRegistrationHomeOwnersIF[],
  location: {
    parkName: string,
    pad: number,
    address: {
      street: string,
      city: string,
      region: string,
      country: string,
      postalCode: string
    }
  },
  description: MhrRegistrationDescriptionIF,
  notes: [
    {
      documentType: string,
      documentId: string,
      createDateTime: string,
      remarks: string,
      contactName: string,
      contactAddress: {
        street: string,
        city: string,
        region: string,
        postalCode: string,
        country: string
      }
    }
  ],
  reviewing: boolean
}
