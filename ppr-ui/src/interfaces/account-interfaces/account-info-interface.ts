import type { AddressIF } from '../ppr-api-interfaces'

export interface AccountAdminInfoIF {
  firstName: string
  lastName: string
  email: string
  phone: string
  phoneExtension: string
}

export interface AccountInfoIF {
  id: number // account Id
  isBusinessAccount: boolean
  name: string // account name or business name
  mailingAddress: AddressIF
  accountAdmin: AccountAdminInfoIF
  phoneNumber?: string
  phoneExtension?: string
}

export interface PaymentInfoIF {
  accountId: string
  accountName: string
  billable: boolean
  credit: number
  id: number
  padTosAcceptedBy: string
  padTosAcceptedDate: string
  paymentMethod: string
  version: number
}
