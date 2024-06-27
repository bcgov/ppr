interface Description {
  baseInformation?: {
    circa?: boolean
    make?: string
    model?: string
    year?: number
  }
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
  sections?: Section[]
  status?: string
}

interface Section {
  lengthFeet?: number
  lengthInches?: number
  serialNumber?: string
  widthFeet?: number
  widthInches?: number
}

interface Address {
  city?: string
  country?: string
  postalCode?: string
  region?: string
  street?: string
}

interface Location {
  address?: Address
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
}

interface IndividualName {
  first?: string
  last?: string
  middle?: string
}

interface Owner {
  address?: Address
  createDateTime?: string
  documentId?: string
  documentRegistrationNumber?: string
  endDateTime?: string
  endRegistrationDescription?: string
  groupCount?: number
  groupId?: number
  groupOwnerCount?: number
  groupTenancyType?: string
  individualName?: IndividualName
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

interface Registration {
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
  descriptions?: Description[]
  locations?: Location[]
  mhrNumber: string
  owners?: Owner[]
  registrations?: Registration[]
  statusType: string
}
