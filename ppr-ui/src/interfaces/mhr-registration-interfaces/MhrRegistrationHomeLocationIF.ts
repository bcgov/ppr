import { HomeLocationTypes } from '@/enums'

export interface MhrRegistrationHomeLocationIF extends MhrRegistrationHomeLocationWithoutAddressIF {
  address: {
    street: string
    streetAdditional?: string
    city: string
    region: string
    country: string
    postalCode: string
  }
}

export interface MhrRegistrationHomeLocationWithoutAddressIF {
  parkName?: string
  pad?: string
  leaveProvince?: boolean
  pidNumber?: string
  taxCertificate?: boolean
  taxExpiryDate?: string
  dealerName?: string
  additionalDescription?: string
  legalDescription?: string
  locationType?: HomeLocationTypes // For local mapping only
  otherType?: HomeLocationTypes // For local mapping only
  lot?: string
  parcel?: string
  block?: string
  districtLot?: string
  partOf?: string
  section?: string
  township?: string
  range?: string
  meridian?: string
  landDistrict?: string
  plan?: string
  bandName?: string
  reserveNumber?: string
  exceptionPlan?: string
  permitWithinSamePark?: boolean // for transport permit amendment
}
