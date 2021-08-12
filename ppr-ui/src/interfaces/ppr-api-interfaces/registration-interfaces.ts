import { GeneralCollateralIF, PartyIF, VehicleCollateralIF } from '@/interfaces'
import { ErrorIF } from './error-interface'

// Payment (pay-api) reference interface.
export interface PaymentIF {
  invoiceId: string, // Unique identifier of the payment transaction.
  receipt: string // Payment API URI to obtain the payment receipt.
}

// Financing Statement interface. All dates/date time properties are in the ISO 8601 format YYYY-MM-DDThh:mm:ssTZD.
export interface FinancingStatementIF {
  type: string, // One of enum APIRegistrationTypes.
  clientReferenceId?: string, // AKA folio max length 20.
  documentId?: string, // Optional draft ID if draft created.
  registrationDescription?: string, // Returned on creation.
  registrationAct?: string, // Returned on creation.
  registeringParty: PartyIF,
  securedParties: PartyIF[],
  debtors: PartyIF[],
  vehicleCollateral?: VehicleCollateralIF[], // Either vehicle or general collatera is required.
  generalCollateral?: GeneralCollateralIF[], // Max length 4000, currently only 1 for a new registration.
  trustIndenture?: boolean, // Conditionally required by registration type.
  lifeInfinite?: boolean,
  lifeYears?: number, // 1..25 if not lifeInfinite, otherwise 0.
  lienAmount?: string, // RL only
  surrenderDate?: string, // RL only
  expiryDate?: string, // The date and time upon which the statement will expire. Empty if lifeInfinite true.
  baseRegistrationNumber?: string, // Included in a successful response. The identifier for the registration.
  createDateTime?: string, // Included in a successful response.
  payment?: PaymentIF, // Included in a successful response.
  error?: ErrorIF
}

// Draft interface. TODO: add change, amendment statement draft definitions when available.
export interface DraftIF {
    type: string, // One of enum DraftTypes.
    financingStatement?: FinancingStatementIF, // Include if draft is for a financing statement.
    createDateTime?: string, // Included in a successful response. Generated on first draft save.
    lastUpdateDateTime?: string, // Included in a successful response. Timestamp of last draft update.
    error?: ErrorIF
}

export interface DraftResultIF {
  type: string, // One of enum DraftTypes.
  documentId?: string,
  baseRegistrationNumber?: string,
  registrationType: string,
  registrationDescription: string,
  path: string,
  createDateTime?: string, // Included in a successful response. Generated on first draft save.
  lastUpdateDateTime?: string, // Included in a successful response. Timestamp of last draft update.
  clientReferenceId: string,
  error?: ErrorIF
}

// Financing Statement registration interface.
// All dates/date time properties are in the ISO 8601 format YYYY-MM-DDThh:mm:ssTZD.
export interface RegistrationSummaryIF {
  registrationNumber: string,
  clientReferenceId?: string, // AKA folio max length 20.
  registrationType: string, // One of enum APIRegistrationTypes.
  registrationDescription?: string, // Returned on creation.
  registrationClass?: string, // Returned on creation.
  registeringParty: string,
  securedParties: string,
  expireDays?: string, // Number of days until expiry
  statusType?: string,
  path: string,
  baseRegistrationNumber?: string, // Included in a successful response. The identifier for the registration.
  createDateTime?: string, // Included in a successful response.
  lastUpdateDateTime?: string, // Included in a successful response. Timestamp of last draft update.
  error?: ErrorIF,
  hide?: boolean
}
