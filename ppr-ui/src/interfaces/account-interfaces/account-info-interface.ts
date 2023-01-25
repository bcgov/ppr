import { AddressIF } from '../ppr-api-interfaces'

export interface AccountInfoIF {
  id: number // account Id
  isBusinessAccount: boolean
  name: string // account name or business name
  mailingAddress: AddressIF
  accountAdmin: AccountAdminInfoIF
}

export interface AccountAdminInfoIF {
  firstName: string
  lastName: string
  email: string
  phone: string
  phoneExtension: string
}
