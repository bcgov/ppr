import { RegistrationFlowType } from '@/enums'
import {
  AccountInformationIF, AuthorizationIF, RegistrationTypeIF, SearchResponseIF,
  SearchTypeIF, UserInfoIF
} from '@/interfaces'
import { AccountProductSubscriptionIF } from '../account-interfaces'
import { CourtOrderIF, DebtorNameIF, DraftIF, IndividualNameIF } from '../ppr-api-interfaces'
import { AddPartiesIF, AddCollateralIF, LengthTrustIF } from '../registration-interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  accountProductSubscriptions: AccountProductSubscriptionIF
  authorization: AuthorizationIF
  folioOrReferenceNumber: string
  registration: {
    amendmentDescription: string // amendments only
    collateral: AddCollateralIF
    confirmDebtorName: DebtorNameIF // Required for actions on existing registrations.
    courtOrderInformation: CourtOrderIF
    creationDate: string
    draft: DraftIF,
    expiryDate: string
    registrationFlowType: RegistrationFlowType
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
    registrationNumber: string
    registrationType: RegistrationTypeIF
    registrationTypeOtherDesc: string
    showStepErrors: boolean
  }
  // for amendments only
  originalRegistration: {
    collateral: AddCollateralIF
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
  }
  search: {
    searchDebtorName: IndividualNameIF
    searchHistory: Array<SearchResponseIF>
    searchResults: SearchResponseIF
    searchedType: SearchTypeIF
    searchedValue: string
    searching: boolean
  }
  userInfo: UserInfoIF
}
