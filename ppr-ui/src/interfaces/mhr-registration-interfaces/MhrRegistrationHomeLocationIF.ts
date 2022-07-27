import { HomeLocationTypes } from '@/enums'

export interface MhrRegistrationHomeLocationIF {
  parkName: string,
  pad: string,
  address: {
    street: string,
    city: string,
    region: string,
    country: string,
    postalCode: string
  },
  leaveProvince: boolean,
  pidNumber: string,
  taxCertificate: boolean,
  dealerName: string,
  additionalDescription: string,
  locationType: HomeLocationTypes, // For local mapping only
  otherType: HomeLocationTypes // For local mapping only
}
