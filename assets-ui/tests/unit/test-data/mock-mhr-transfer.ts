import { ApiHomeTenancyTypes, HomeOwnerPartyTypes } from '@/enums'
import {
  AddressIF,
  MhRegistrationSummaryIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'

export const mockMhrTransferCurrentHomeOwner = {
  groupId: 1,
  interest: 'Undivided',
  interestNumerator: 1,
  interestDenominator: 1,
  owners: [
    {
      address: {
        city: 'KELOWNA',
        country: 'CA',
        postalCode: 'V1X7T1',
        region: 'BC',
        street: '3075 SEXSMITH ROAD'
      } as AddressIF,
      organizationName: 'CHAPARRAL INDUSTRIES (86) INC.',
      phoneNumber: '2507652985',
      phoneExtension: '1234',
      type: 'SOLE'
    } as MhrRegistrationHomeOwnerIF
  ],
  status: 'PREVIOUS',
  tenancySpecified: true,
  type: 'SOLE'
} as MhrRegistrationHomeOwnerGroupIF

export const mockMhrTransferCurrentHomeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
  {
    groupId: 5,
    interest: 'UNDIVIDED',
    interestDenominator: 2,
    interestNumerator: 1,
    owners: [
      {
        address: {
          city: 'V4V 4V4',
          country: 'CA',
          postalCode: 'v4v 4v4',
          region: 'BC',
          street: '123123',
          streetAdditional: 'VICTORIA V4V 4V4 V4V 4V4 V4V 4V4'
        },
        individualName: { first: 'JAMES', last: 'TESTING' },
        ownerId: 1,
        partyType: HomeOwnerPartyTypes.OWNER_IND,
        phoneNumber: '1123123123',
        type: ApiHomeTenancyTypes.JOINT

      } as MhrRegistrationHomeOwnerIF,
      {
        address: { city: 'VANCOUVER', country: 'CA', postalCode: 'V6B 2L2', region: 'BC', street: '555-455 ABBOTT ST' },
        individualName: { first: 'NEW', last: 'PERSON' },
        ownerId: 2,
        partyType: 'OWNER_IND',
        type: ApiHomeTenancyTypes.JOINT
      } as MhrRegistrationHomeOwnerIF
    ],
    tenancySpecified: true,
    type: 'JOINT'
  },
  {
    groupId: 6,
    interest: 'UNDIVIDED',
    interestDenominator: 2,
    interestNumerator: 1,
    owners: [
      {
        address: {
          city: 'V4V 4V4',
          country: 'CA',
          postalCode: 'v4v 4v4',
          region: 'BC',
          street: '123123',
          streetAdditional: 'VICTORIA'
        },
        individualName: { first: 'JOE', last: 'TESTING' },
        ownerId: 3,
        partyType: HomeOwnerPartyTypes.OWNER_IND,
        phoneNumber: '1123123123',
        type: ApiHomeTenancyTypes.COMMON
      } as MhrRegistrationHomeOwnerIF
    ],
    tenancySpecified: true,
    type: 'COMMON'
  }
]

export const mockMhrTransferDraft = {
  inUserList: true, // whether the registration is in their table or not
  error: null,
  clientReferenceId: '',
  createDateTime: '',
  draftNumber: '',
  mhrNumber: '253333',
  ownerNames: 'testo1, testo2',
  path: '',
  registrationDescription: 'REGISTER NEW UNIT',
  statusType: 'Draft',
  submittingParty: 'submitting party',
  username: 'user 1',
  baseRegistrationNumber: '253333',
  changes: [{
    inUserList: true, // whether the registration is in their table or not
    error: null,
    clientReferenceId: '',
    createDateTime: '',
    draftNumber: '',
    mhrNumber: '253333',
    ownerNames: 'testo1, testo2',
    path: '',
    registrationDescription: 'REGISTER NEW UNIT',
    statusType: 'Draft',
    submittingParty: 'submitting party',
    username: 'user 1',
    baseRegistrationNumber: '253333',
    changes: null,
    hasDraft: true
  } as MhRegistrationSummaryIF],
  hasDraft: true
} as MhRegistrationSummaryIF
