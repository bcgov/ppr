import { AddressIF, MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'

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
  owners: []
}

export const mockedPerson: MhrRegistrationHomeOwnerIF = {
  id: '10',
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '5453332211',
  phoneExtension: '1234',
  address: mockedAddress
}

export const mockedOrganization: MhrRegistrationHomeOwnerIF = {
  id: '20',
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '9998887766',
  phoneExtension: '4321',
  address: mockedAddressAlt
}
