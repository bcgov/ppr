import { StaffPaymentOptions } from '@/enums'

export * from './account-interfaces'
export * from './breadcrumb-interface'
export * from './error-interface'
export * from './data-table-interfaces'
export * from './date-picker-interfaces'
export * from './dialog-inerfaces'
export * from './mhr-registration-interfaces'
export * from './party-interfaces'
export * from './pay-api-interfaces'
export * from './ppr-api-interfaces'
export * from './registration-interfaces'
export * from './search-interfaces'
export * from './store-interfaces'
export * from './state-interface'
export * from './account-interface'
export * from './validation-interfaces'
export * from './von-api-interfaces'
export * from './steps-interface'
export * from './product-interfaces'
export * from './registries-search-api-interface'
export * from './content-interface'
export * from './unit-note-interfaces'
export * from './mhr-user-access-interfaces'
export * from './user-access-interfaces'
export * from './exemption-interfaces'
export * from './base-data-union-interface'
export * from './updated-badge-interface'
export * from './admin-registration-interfaces'

/** A filing's business object from the API. */
export interface StaffPaymentIF {
  option: StaffPaymentOptions
  routingSlipNumber: string
  bcolAccountNumber: string
  datNumber: string
  folioNumber: string
  isPriority: boolean
}
