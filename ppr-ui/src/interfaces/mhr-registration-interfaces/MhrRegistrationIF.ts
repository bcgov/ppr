import { HomeSectionIF } from '@/interfaces'

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
  owners: [
    {
      individualName: {
        first: string,
        last: string
      },
      address: {
        street: string,
        city: string,
        region: string,
        country: string,
        postalCode: string
      },
      type: string
    }
  ],
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
  description: {
    manufacturer: string,
    baseInformation: {
        year: number,
        make: string,
        model: string
    },
    sectionCount: number,
    sections: Array<HomeSectionIF>,
    csaNumber: number,
    csaStandard: string
  },
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
  ]
}
