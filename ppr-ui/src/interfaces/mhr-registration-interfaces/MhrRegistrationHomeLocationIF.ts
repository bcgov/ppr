import { HomeLocationTypes } from '@/enums'

export interface MhrRegistrationHomeLocationIF {
  parkName: string
  pad: string
  address: {
    street: string
    streetAdditional: string
    city: string
    region: string
    country: string
    postalCode: string
  }
  leaveProvince: boolean
  pidNumber: string
  taxCertificate: boolean
  dealerName: string
  additionalDescription: string
  legalDescription: string
  locationType: HomeLocationTypes // For local mapping only
  otherType: HomeLocationTypes // For local mapping only
  parcel: string
  block: string
  districtLot: string
  partOf: string
  section: string
  township: string
  range: string
  meridian: string
  landDistrict: string
  plan: string
  bandName: string
  reserveNumber: string
  exceptPlan: string
}
