import { AddressIF, MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnersIF } from '@/interfaces'

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
  groupId: '100',
  owners: [],
  type: 'SO' // TODO: Mhr-Submission - UPDATE after the correct type can be determined
}

export const mockedPerson: MhrRegistrationHomeOwnersIF = {
  id: '10',
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

export const mockedOrganization: MhrRegistrationHomeOwnersIF = {
  id: '20',
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  address: mockedAddressAlt
}
