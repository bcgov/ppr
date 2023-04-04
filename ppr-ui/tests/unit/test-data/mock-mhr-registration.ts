import { ActionTypes, HomeTenancyTypes } from '@/enums'
import {
  AddressIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'

export const mockedAddress: AddressIF = {
  street: '1234 Fort St.',
  streetAdditional: '2nd floor',
  city: 'Victoria',
  region: 'BC',
  country: 'CA',
  postalCode: 'V8R1L2',
  deliveryInstructions: 'Back Door'
}

export const mockedAddressAlt: AddressIF = {
  street: '1234 Fort St.',
  streetAdditional: '3rd floor',
  city: 'Nanaimo',
  region: 'BC',
  country: 'CA',
  postalCode: 'V6L4K4',
  deliveryInstructions: 'Front Door'
}

export const mockedEmptyGroup: MhrRegistrationHomeOwnerGroupIF = {
  groupId: 100,
  owners: [],
  // TODO: Mhr-Submission - UPDATE after the correct type can be determined
  type: Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === HomeTenancyTypes.SOLE)
}

export const mockedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  address: mockedAddress
}

export const mockedAddedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  address: mockedAddress,
  action: ActionTypes.ADDED
}

export const mockedRemovedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  address: mockedAddress,
  action: ActionTypes.REMOVED
}

export const mockedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  address: mockedAddressAlt
}

export const mockedAddedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  address: mockedAddressAlt,
  action: ActionTypes.ADDED
}

export const mockedRemovedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  address: mockedAddressAlt,
  action: ActionTypes.REMOVED
}

export const mockedFractionalOwnership: MhrRegistrationFractionalOwnershipIF = {
  interest: 'Undivided',
  interestNumerator: 1,
  interestDenominator: 4
}
