import { AccountInfoIF, AddressIF } from '@/interfaces'
import { mockedAddress } from './mock-mhr-registration'

export const mockedAccountInfo: AccountInfoIF = {
  id: 2573,
  isBusinessAccount: false,
  name: 'PPR 2',
  mailingAddress: mockedAddress as AddressIF,
  accountAdmin: {
    firstName: 'BCREG2',
    lastName: 'BCREG222',
    email: 'ppr@email.com',
    phone: '(123) 456-7890',
    phoneExtension: '444'
  }
}
