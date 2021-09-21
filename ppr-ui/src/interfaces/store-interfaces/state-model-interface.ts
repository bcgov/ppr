import { RegistrationFlowType } from '@/enums'
import {
  AccountInformationIF, AuthorizationIF, RegistrationTypeIF, SearchResponseIF,
  SearchTypeIF, UserInfoIF
} from '@/interfaces'
import { AccountProductSubscriptionIF } from '../account-interfaces'
import { DebtorNameIF, DraftIF, IndividualNameIF } from '../ppr-api-interfaces'
import { AddPartiesIF, AddCollateralIF, LengthTrustIF } from '../registration-interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  accountProductSubscriptions: AccountProductSubscriptionIF
  authorization: AuthorizationIF
  folioOrReferenceNumber: string
  registration: {
    collateral: AddCollateralIF
    confirmDebtorName: DebtorNameIF // Required for registrations.
    creationDate: string
    currentStep: number,
    debtorName: IndividualNameIF
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
  search: {
    searchHistory: Array<SearchResponseIF>
    searchResults: SearchResponseIF
    searchedType: SearchTypeIF
    searchedValue: string
    searching: boolean
  }
  userInfo: UserInfoIF
}
