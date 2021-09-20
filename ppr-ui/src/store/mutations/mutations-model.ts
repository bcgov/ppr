import { RegistrationFlowType } from '@/enums'
import {
  AccountInformationIF,
  AddCollateralIF,
  AddPartiesIF,
  DebtorNameIF,
  DraftIF,
  LengthTrustIF,
  IndividualNameIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  UserInfoIF,
  UserSettingsIF,
  AccountProductSubscriptionIF
} from '@/interfaces'

export const mutateAccountProductSubscribtion = (
  state: StateIF, productSubscriptions: AccountProductSubscriptionIF
) => {
  state.stateModel.accountProductSubscriptions = productSubscriptions
}

export const mutateAccountInformation = (state: StateIF, accountInformation: AccountInformationIF) => {
  state.stateModel.accountInformation = accountInformation
}

export const mutateAddCollateral = (state: StateIF, addCollateral: AddCollateralIF) => {
  state.stateModel.registration.collateral = addCollateral
}

export const mutateAddSecuredPartiesAndDebtors = (state: StateIF, addParties: AddPartiesIF) => {
  state.stateModel.registration.parties = addParties
}

export const mutateAuthRoles = (state: StateIF, authRoles: Array<string>) => {
  state.stateModel.authorization.authRoles = authRoles
}

export const mutateCurrentStep = (state: any, currentStep: boolean) => {
  state.stateModel.registration.currentStep = currentStep
}

export const mutateDebtorName = (state: StateIF, debtorName: IndividualNameIF) => {
  state.stateModel.registration.debtorName = debtorName
}

export const mutateDraft = (state: StateIF, draft: DraftIF) => {
  state.stateModel.registration.draft = draft
}

export const mutateKeycloakRoles = (state: StateIF, keyCloakRoles: Array<string>) => {
  state.stateModel.authorization.keycloakRoles = keyCloakRoles
}

export const mutateLengthTrust = (state: StateIF, lengthTrust: LengthTrustIF) => {
  state.stateModel.registration.lengthTrust = lengthTrust
}

export const mutateNewRegistration = (state: StateIF) => {
  state.stateModel.registration.showStepErrors = false
  state.stateModel.registration.lengthTrust.valid = false
  state.stateModel.registration.lengthTrust.showInvalid = false
  state.stateModel.registration.lengthTrust.lifeInfinite = false
  state.stateModel.registration.lengthTrust.trustIndenture = false
  state.stateModel.registration.lengthTrust.lifeYears = 0
  state.stateModel.registration.lengthTrust.lienAmount = ''
  state.stateModel.registration.lengthTrust.surrenderDate = ''
  state.stateModel.registration.collateral.valid = false
  state.stateModel.registration.collateral.generalCollateral = []
  state.stateModel.registration.collateral.vehicleCollateral = []
  state.stateModel.registration.parties.valid = false
  state.stateModel.registration.parties.registeringParty = null
  state.stateModel.registration.parties.securedParties = []
  state.stateModel.registration.parties.debtors = []
  state.stateModel.registration.draft = {
    type: '',
    financingStatement: null,
    createDateTime: null,
    lastUpdateDateTime: null
  }
  state.stateModel.registration.confirmDebtorName = null
}

export const mutateRegistrationConfirmDebtorName = (state: StateIF, debtorName: DebtorNameIF) => {
  state.stateModel.registration.confirmDebtorName = debtorName
}

export const mutateRegistrationCreationDate = (state: StateIF, date: string) => {
  state.stateModel.registration.creationDate = date
}

export const mutateRegistrationExpiryDate = (state: StateIF, date: string) => {
  state.stateModel.registration.expiryDate = date
}

export const mutateRegistrationNumber = (state: StateIF, regNum: string) => {
  state.stateModel.registration.registrationNumber = regNum
}

export const mutateRegistrationType = (state: StateIF, registrationType: RegistrationTypeIF) => {
  state.stateModel.registration.registrationType = registrationType
}

export const mutateRegistrationFlowType = (state: StateIF, registrationFlowType: RegistrationFlowType) => {
  state.stateModel.registration.registrationFlowType = registrationFlowType
}

export const mutateRegistrationTypeOtherDesc = (state: StateIF, description: string) => {
  state.stateModel.registration.registrationTypeOtherDesc = description
}

export const mutateSearchedType = (state: StateIF, searchedType: SearchTypeIF) => {
  state.stateModel.search.searchedType = searchedType
}

export const mutateSearchedValue = (state: StateIF, searchedValue: string) => {
  state.stateModel.search.searchedValue = searchedValue
}

export const mutateSearching = (state: StateIF, searching: boolean) => {
  state.stateModel.search.searching = searching
}

export const mutateSearchHistory = (state: StateIF, searchHistory: Array<SearchResponseIF>) => {
  state.stateModel.search.searchHistory = searchHistory
}

export const mutateSearchResults = (state: StateIF, searchResults: SearchResponseIF) => {
  state.stateModel.search.searchResults = searchResults
}

export const mutateUserInfo = (state: StateIF, userInfo: UserInfoIF) => {
  state.stateModel.userInfo = userInfo
}

export const mutateUserSettings = (state: StateIF, settings: UserSettingsIF) => {
  state.stateModel.userInfo.settings = settings
}

export const mutateAddSecuredPartiesAndDebtorStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.parties.valid = validity
}

export const mutateAddCollateralStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.collateral.valid = validity
}

export const mutateLengthTrustStepValidity = (state: any, validity: boolean) => {
  state.stateModel.registration.lengthTrust.valid = validity
}

export const mutateFolioOrReferenceNumber = (state: StateIF, refNumber: string) => {
  state.stateModel.folioOrReferenceNumber = refNumber
}

export const mutateShowStepErrors = (state: any, show: boolean) => {
  state.stateModel.registration.showStepErrors = show
}
