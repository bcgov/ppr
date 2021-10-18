import { APIAmendmentTypes, APIRegistrationTypes } from '@/enums'
import { CourtOrderIF, DebtorNameIF, GeneralCollateralIF, PartyIF, VehicleCollateralIF } from '@/interfaces'
import { ErrorIF } from './error-interface'

// Payment (pay-api) reference interface.
export interface PaymentIF {
  invoiceId: string, // Unique identifier of the payment transaction.
  receipt: string // Payment API URI to obtain the payment receipt.
}

// Financing Statement interface. All dates/date time properties are in the ISO 8601 format YYYY-MM-DDThh:mm:ssTZD.
export interface FinancingStatementIF {
  type: APIRegistrationTypes, // One of enum APIRegistrationTypes.
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
  otherTypeDescription?: string, // Included if type is Other
  error?: ErrorIF
}

// Draft interface. Change statement draft is out of scope.
export interface DraftIF {
    type: string, // One of enum DraftTypes.
    financingStatement?: FinancingStatementIF, // Include if draft is for a financing statement.
    amendmentStatement?: AmendmentStatementIF, // Include if draft is for an amendment statement.
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
  inUserList?: boolean, // whether the registration is in their table or not
  registrationNumber: string,
  clientReferenceId?: string, // AKA folio max length 20.
  registrationType: string, // One of enum APIRegistrationTypes.
  registrationDescription?: string, // Returned on creation.
  registrationClass?: string, // Returned on creation.
  registeringParty: string,
  securedParties: string,
  expireDays?: number, // Number of days until expiry
  statusType?: string,
  path: string,
  baseRegistrationNumber?: string, // Included in a successful response. The identifier for the registration.
  createDateTime?: string, // Included in a successful response.
  lastUpdateDateTime?: string, // Included in a successful response. Timestamp of last draft update.
  error?: ErrorIF,
  hide?: boolean
}

// Discharge Registration interface. Base registration number, debtor name, and registering party are required.
export interface DischargeRegistrationIF {
  baseRegistrationNumber: string, // The identifier of the financing statement being discharged.
  debtorName: DebtorNameIF,
  registeringParty: PartyIF,
  clientReferenceId?: string, // AKA folio max length 20.
  dischargeRegistrationNumber?: string, // Included on success, the identifier for the discharge registration.
  createDateTime?: string, // Included in a successful response.
  payment?: PaymentIF, // Included in a successful response.
  error?: ErrorIF // Not null if the API call is unsuccessful.
}

// Renew registration interface. Slightly guessing on the fields here
export interface RenewRegistrationIF {
  baseRegistrationNumber: string, // The identifier of the financing statement being discharged.
  debtorName: DebtorNameIF,
  registeringParty: PartyIF,
  clientReferenceId?: string, // AKA folio max length 20.
  lifeInfinite?: boolean,
  lifeYears?: number, // 1..25 if not lifeInfinite, otherwise 0.
  expiryDate?: string, // The date and time upon which the statement will expire. Empty if lifeInfinite true.
  renewalRegistrationNumber?: string,
  createDateTime?: string, // Included in a successful response.
  payment?: PaymentIF, // Included in a successful response.
  error?: ErrorIF
}

// Amendment Statement interface. All dates/date time properties are in the ISO 8601 format YYYY-MM-DDThh:mm:ssTZD.
export interface AmendmentStatementIF {
  changeType?: APIAmendmentTypes, // Mandatory, can save draft without it.
  clientReferenceId?: string, // AKA folio max length 20.
  documentId?: string, // Optional draft ID if draft created.
  description?: string, // Mandatory description of amendment, can save draft without it.
  baseRegistrationNumber: string, // The identifier of the registration being amended.
  debtorName: DebtorNameIF, // Mandatory name of current debtor.
  registeringParty?: PartyIF, // Mandatory, can save draft without it.
  courtOrderInformation?: CourtOrderIF, // Only populated if all court order elements present.
  addSecuredParties?: PartyIF[], // Only populated if adding.
  deleteSecuredParties?: PartyIF[], // Only populated if deleting.
  addDebtors?: PartyIF[], // Only populated if adding.
  deleteDebtors?: PartyIF[], // Only populated if deleting.
  addVehicleCollateral?: VehicleCollateralIF[], // Only populated if adding.
  deleteVehicleCollateral?: VehicleCollateralIF[], // Only populated if deleting.
  addGeneralCollateral?: GeneralCollateralIF[], // Only populated if adding.
  deleteGeneralCollateral?: GeneralCollateralIF[], // Only populated if deleting.
  addTrustIndenture?: boolean, // Include if adding a trust indenture for a SA.
  removeTrustIndenture?: boolean, // Include if removing a trust indenture for a SA.
  createDateTime?: string, // Included in a successful response.
  amendmentRegistrationNumber?: string, // Included in a successful response. The unique identifier of the registration.
  payment?: PaymentIF, // Included in a successful response.
  error?: ErrorIF
}
