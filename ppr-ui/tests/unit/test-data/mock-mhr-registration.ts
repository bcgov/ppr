import { ActionTypes, HomeTenancyTypes, HomeOwnerPartyTypes } from '@/enums'
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

export const mockedExecutor: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Executor of the will of John Smith',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.EXECUTOR,
  address: mockedAddress
}

export const mockedOwner: MhrRegistrationHomeOwnerIF = {
  ownerId: 45,
  individualName: {
    first: 'Owner',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'I am an owner!',
  phoneNumber: '(123) 777-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress
}

export const mockedAddedExecutor: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.EXECUTOR,
  action: ActionTypes.ADDED,
  address: mockedAddress
}

export const mockedAdministrator: MhrRegistrationHomeOwnerIF = {
  ownerId: 35,
  individualName: {
    first: 'Admin',
    middle: 'M',
    last: 'Smith'
  },
  description: 'ADMINISTRATOR 123',
  phoneNumber: '(123) 777-6666',
  phoneExtension: '7656',
  partyType: HomeOwnerPartyTypes.ADMINISTRATOR,
  address: mockedAddress
}

export const mockedAddedAdministrator: MhrRegistrationHomeOwnerIF = {
  ownerId: 30,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.ADMINISTRATOR,
  action: ActionTypes.ADDED,
  address: mockedAddress
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
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress
}

export const mockedPerson2: MhrRegistrationHomeOwnerIF = {
  ownerId: 11,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
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
