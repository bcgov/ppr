import type { ProductCode, RegistrationFlowType } from '@/enums'
import type {
  AddPartiesIF,
  AddCollateralIF,
  CourtOrderIF,
  DebtorNameIF,
  DraftIF,
  IndividualNameIF,
  ManufacturedHomeSearchResponseIF,
  ManufacturedHomeSearchResultIF,
  LengthTrustIF,
  AccountProductSubscriptionIF,
  AccountInformationIF,
  AuthorizationIF,
  CertifyIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  SortOptionIF,
  RegTableDataI,
  UserInfoIF,
  MhrRegistrationIF,
  UserProductSubscriptionIF,
  MhrValidationStateIF,
  MhrTransferIF,
  MhRegistrationSummaryIF,
  mhrInfoValidationStateIF,
  MhrValidationManufacturerStateIF,
  UnitNoteRegistrationIF,
  MhrUnitNoteValidationStateIF,
  UserAccessIF,
  UserAccessValidationIF,
  ExemptionIF,
  ExemptionValidationIF,
  StaffPaymentIF,
  MhrTransportPermitIF,
  AddEditSaNoticeIF,
  MhrRegistrationHomeOwnerGroupIF,
  PaymentInfoIF
} from '@/interfaces'
import type { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  isAccountAdministrator: boolean
  accountProductSubscriptions: AccountProductSubscriptionIF
  accountPaymentInformation: PaymentInfoIF
  userProductSubscriptions: Array<UserProductSubscriptionIF>
  userProductSubscriptionsCodes: Array<ProductCode>
  authorization: AuthorizationIF
  certifyInformation: CertifyIF
  folioOrReferenceNumber: string
  generateDocId:boolean
  // for amendments only
  originalRegistration: {
    collateral: AddCollateralIF
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
    securitiesActNotices?: Array<AddEditSaNoticeIF>
  }
  registration: {
    amendmentDescription: string // amendments only
    collateral: AddCollateralIF
    confirmDebtorName: DebtorNameIF // Required for actions on existing registrations.
    courtOrderInformation: CourtOrderIF
    creationDate: string
    draft: DraftIF
    expiryDate: string
    registrationFlowType: RegistrationFlowType
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
    registrationNumber: string
    registrationType: RegistrationTypeIF | null
    registrationTypeOtherDesc: string
    showStepErrors: boolean
    transitioned?: boolean
    securitiesActNotices?: Array<AddEditSaNoticeIF>
  }
  registrationTable: RegTableDataI
  search: {
    searchDebtorName: IndividualNameIF
    searchHistory: Array<SearchResponseIF>
    searchHistoryLength: number
    searchResults: SearchResponseIF
    manufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF
    searchedType: SearchTypeIF
    searchedValue: string
    searching: boolean
    searchCertified: boolean
  }
  selectedManufacturedHomes: ManufacturedHomeSearchResultIF[]
  mhrSearchResultSortOption: SortOptionIF
  isStaffClientPayment: boolean
  staffPayment: StaffPaymentIF
  unsavedChanges: boolean // used for cancel flows
  currentRegistrationsTab: number
  userInfo: UserInfoIF
  mhrInformation: MhRegistrationSummaryIF
  mhrRegistration: MhrRegistrationIF
  mhrReRegistrationPreviousOwnerGroups?: MhrRegistrationHomeOwnerGroupIF[]
  mhrReRegistrationPreviousTenancyType?: string
  mhrBaseline?: MhrRegistrationIF
  mhrUnitNotes?: Array<UnitNoteIF>
  mhrUnitNote: UnitNoteRegistrationIF // used for Unit Note filing/registration
  mhrUnitNoteValidationState: MhrUnitNoteValidationStateIF
  mhrUserAccess: UserAccessIF
  mhrExemption: ExemptionIF
  mhrExemptionValidation: ExemptionValidationIF
  mhrUserAccessValidation: UserAccessValidationIF
  mhrSearchResultSelectAllLien: boolean
  mhrValidationState?: MhrValidationStateIF
  mhrValidationManufacturerState?: MhrValidationManufacturerStateIF
  mhrTransfer: MhrTransferIF
  mhrInfoValidationState: mhrInfoValidationStateIF
  mhrTransportPermit: MhrTransportPermitIF
  mhrOriginalTransportPermit?: MhrTransportPermitIF // original Transport Permit filing when working with Amendments
}
