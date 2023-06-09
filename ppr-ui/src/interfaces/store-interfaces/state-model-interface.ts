import { ProductCode, RegistrationFlowType } from '@/enums'
import {
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
  RegTableDataI,
  UserInfoIF,
  MhrRegistrationIF,
  UserProductSubscriptionIF,
  MhrValidationStateIF,
  MhrTransferIF,
  MhRegistrationSummaryIF,
  mhrInfoValidationStateIF,
  MhrValidationManufacturerStateIF,
  UnitNoteRegistrationIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  accountProductSubscriptions: AccountProductSubscriptionIF
  userProductSubscriptions: Array<UserProductSubscriptionIF>
  userProductSubscriptionsCodes: Array<ProductCode>,
  authorization: AuthorizationIF
  certifyInformation: CertifyIF
  folioOrReferenceNumber: string
  // for amendments only
  originalRegistration: {
    collateral: AddCollateralIF
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
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
  isStaffClientPayment: boolean
  staffPayment: StaffPaymentIF
  unsavedChanges: boolean // used for cancel flows
  currentRegistrationsTab: number
  userInfo: UserInfoIF
  mhrInformation: MhRegistrationSummaryIF
  mhrRegistration: MhrRegistrationIF
  mhrUnitNotes?: Array<UnitNoteIF>
  mhrUnitNote: UnitNoteRegistrationIF // used for Unit Note filing/registration
  mhrSearchResultSelectAllLien: boolean
  mhrValidationState?: MhrValidationStateIF
  mhrValidationManufacturerState?: MhrValidationManufacturerStateIF
  mhrTransfer: MhrTransferIF
  mhrInfoValidationState: mhrInfoValidationStateIF
}
