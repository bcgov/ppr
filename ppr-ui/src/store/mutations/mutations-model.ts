import {
  AccountInformationIF,
  AddCollateralIF,
  AddPartiesIF,
  DraftIF,
  FeeSummaryIF,
  LengthTrustIF,
  IndividualNameIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  UserInfoIF,
  UserSettingsIF
} from '@/interfaces'

export const mutateAccountInformation = (state: StateIF, accountInformation: AccountInformationIF) => {
  state.stateModel.accountInformation = accountInformation
}

export const mutateAddCollateral = (state: StateIF, addCollateral: AddCollateralIF) => {
  state.stateModel.addCollateralStep = addCollateral
}

export const mutateAddSecuredPartiesAndDebtors = (state: StateIF, addParties: AddPartiesIF) => {
  state.stateModel.addSecuredPartiesAndDebtorsStep = addParties
}

export const mutateAuthRoles = (state: StateIF, authRoles: Array<string>) => {
  state.stateModel.authorization.authRoles = authRoles
}

export const mutateCurrentStep = (state: any, currentStep: boolean) => {
  state.stateModel.currentStep = currentStep
}

export const mutateDebtorName = (state: StateIF, debtorName: IndividualNameIF) => {
  state.stateModel.debtorName = debtorName
}

export const mutateDraft = (state: StateIF, draft: DraftIF) => {
  state.stateModel.draft = draft
}

export const mutateFeeSummary = (state: StateIF, feeSummary: FeeSummaryIF) => {
  state.stateModel.feeSummary = feeSummary
}

export const mutateKeycloakRoles = (state: StateIF, keyCloakRoles: Array<string>) => {
  state.stateModel.authorization.keycloakRoles = keyCloakRoles
}

export const mutateLengthTrust = (state: StateIF, lengthTrust: LengthTrustIF) => {
  state.stateModel.lengthTrustStep = lengthTrust
}

export const mutateNewRegistration = (state: StateIF) => {
  state.stateModel.lengthTrustStep.valid = false
  state.stateModel.lengthTrustStep.lifeInfinite = false
  state.stateModel.lengthTrustStep.trustIndenture = false
  state.stateModel.lengthTrustStep.lifeYears = 0
  state.stateModel.feeSummary.feeAmount = 0
  state.stateModel.feeSummary.quantity = 0
  state.stateModel.feeSummary.feeCode = ''
  state.stateModel.addCollateralStep.valid = false
  state.stateModel.addCollateralStep.generalCollateral = ''
  state.stateModel.addCollateralStep.vehicleCollateral = []
  state.stateModel.addSecuredPartiesAndDebtorsStep.valid = false
  state.stateModel.addSecuredPartiesAndDebtorsStep.registeringParty = null
  state.stateModel.addSecuredPartiesAndDebtorsStep.securedParties = []
  state.stateModel.addSecuredPartiesAndDebtorsStep.debtors = []
  state.stateModel.draft = {
    type: '',
    financingStatement: null,
    createDateTime: null,
    lastUpdateDateTime: null
  }
}

export const mutateRegistrationType = (state: StateIF, registrationType: RegistrationTypeIF) => {
  state.stateModel.registrationType = registrationType
}

export const mutateSearchedType = (state: StateIF, searchedType: SearchTypeIF) => {
  state.stateModel.searchedType = searchedType
}

export const mutateSearchedValue = (state: StateIF, searchedValue: string) => {
  state.stateModel.searchedValue = searchedValue
}

export const mutateSearching = (state: StateIF, searching: boolean) => {
  state.stateModel.searching = searching
}

export const mutateSearchHistory = (state: StateIF, searchHistory: Array<SearchResponseIF>) => {
  state.stateModel.searchHistory = searchHistory
}

export const mutateSearchResults = (state: StateIF, searchResults: SearchResponseIF) => {
  state.stateModel.searchResults = searchResults
}

export const mutateUserInfo = (state: StateIF, userInfo: UserInfoIF) => {
  state.stateModel.userInfo = userInfo
}

export const mutateUserSettings = (state: StateIF, settings: UserSettingsIF) => {
  state.stateModel.userInfo.settings = settings
}

export const mutateAddSecuredPartiesAndDebtorStepValidity = (state: any, validity: boolean) => {
  state.stateModel.addSecuredPartiesAndDebtorsStep.valid = validity
}

export const mutateAddCollateralStepValidity = (state: any, validity: boolean) => {
  state.stateModel.addCollateralStep.valid = validity
}

export const mutateLengthTrustStepValidity = (state: any, validity: boolean) => {
  state.stateModel.lengthTrustStep.valid = validity
}
