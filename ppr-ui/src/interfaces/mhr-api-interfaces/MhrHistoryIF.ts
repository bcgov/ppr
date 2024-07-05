import { AddressIF, MhrLocationInfoIF } from '@/interfaces'

export interface DescriptionIF {
  baseInformation?: {
    circa?: boolean
    make?: string
    model?: string
    year?: number
  }
  engineerName?: string
  engineerDate?: string
  createDateTime?: string
  csaNumber?: string
  csaStandard?: string
  documentId?: string
  documentRegistrationNumber?: string
  manufacturer?: string
  otherRemarks?: string
  rebuiltRemarks?: string
  registrationDescription?: string
  sectionCount?: number
  sections?: SectionIF[]
  status?: string
}

export interface SectionIF {
  lengthFeet?: number
  lengthInches?: number
  serialNumber?: string
  widthFeet?: number
  widthInches?: number
}

export interface LocationIF extends MhrLocationInfoIF{
  address?: AddressIF
  additionalDescription?: string
  createDateTime?: string
  documentId?: string
  documentRegistrationNumber?: string
  endDateTime?: string
  endRegistrationDescription?: string
  leaveProvince?: boolean
  legalDescription?: string
  locationId?: number
  locationType?: string
  pidNumber?: string
  registrationDescription?: string
  status?: string
  taxCertificate?: boolean
  dealerName?: string
  parkName?: string
  pad?: string
  isOwnLand?: string
}

export interface IndividualNameIF {
  first?: string
  last?: string
  middle?: string
}

export interface OwnerIF {
  address?: AddressIF
  createDateTime?: string
  documentId?: string
  documentRegistrationNumber?: string
  endDateTime?: string
  endRegistrationDescription?: string
  groupCount?: number
  groupId?: number
  groupOwnerCount?: number
  groupTenancyType?: string
  individualName?: IndividualNameIF
  interest?: string
  interestDenominator?: number
  interestNumerator?: number
  ownerId?: number
  partyType?: string
  phoneNumber?: string
  registrationDescription?: string
  status?: string
  type?: string
}

export interface RegistrationIF {
  affirmByName?: string
  attentionReference?: string
  consideration?: string
  createDateTime?: string
  declaredValue?: number
  documentId?: string
  documentRegistrationNumber?: string
  ownLand?: boolean
  registrationDescription?: string
  transferDate?: string
}

export interface MhrHistoryRoIF {
  descriptions?: DescriptionIF[]
  locations?: LocationIF[]
  mhrNumber: string
  owners?: OwnerIF[]
  registrations?: RegistrationIF[]
  statusType: string
}
