import {
  AccountInformationIF, AuthorizationIF, FeeSummaryIF, RegistrationTypeIF, SearchResponseIF,
  SearchTypeIF, UserInfoIF
} from '@/interfaces'
import { IndividualNameIF } from '../ppr-api-interfaces'
import { AddPartiesIF, AddCollateralIF, LengthTrustIF } from '../registration-interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  authorization: AuthorizationIF
  currentStep: number,
  debtorName: IndividualNameIF
  feeSummary: FeeSummaryIF
  registrationType: RegistrationTypeIF
  searchHistory: Array<SearchResponseIF>
  searchResults: SearchResponseIF
  searchedType: SearchTypeIF
  searchedValue: string
  searching: boolean
  userInfo: UserInfoIF
  lengthTrustStep: LengthTrustIF
  addSecuredPartiesAndDebtorsStep: AddPartiesIF
  addCollateralStep: AddCollateralIF
}
