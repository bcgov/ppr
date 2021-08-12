import {
  AccountInformationIF, AuthorizationIF, FeeSummaryIF, RegistrationTypeIF, SearchResponseIF,
  SearchTypeIF, UserInfoIF
} from '@/interfaces'
import { AccountProductSubscriptionIF } from '../account-interfaces'
import { DraftIF, IndividualNameIF } from '../ppr-api-interfaces'
import { AddPartiesIF, AddCollateralIF, LengthTrustIF } from '../registration-interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  accountProductSubscriptions: AccountProductSubscriptionIF
  authorization: AuthorizationIF
  currentStep: number,
  debtorName: IndividualNameIF
  draft: DraftIF,
  feeSummary: FeeSummaryIF
  registrationType: RegistrationTypeIF
  registrationTypeOtherDesc: string
  searchHistory: Array<SearchResponseIF>
  searchResults: SearchResponseIF
  searchedType: SearchTypeIF
  searchedValue: string
  searching: boolean
  showStepErrors: boolean
  userInfo: UserInfoIF
  lengthTrustStep: LengthTrustIF
  addSecuredPartiesAndDebtorsStep: AddPartiesIF
  addCollateralStep: AddCollateralIF
  folioOrReferenceNumber: string
}
