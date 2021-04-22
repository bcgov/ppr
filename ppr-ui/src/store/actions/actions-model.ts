import {
  AccountInformationIF,
  AddCollateralIF,
  AddPartiesIF,
  FeeSummaryIF,
  LengthTrustIF,
  IndividualNameIF,
  RegistrationTypeIF,
  SearchResponseIF,
  SearchTypeIF,
  UserInfoIF,
  UserSettingsIF
} from '@/interfaces'
import { ActionIF } from '@/interfaces/store-interfaces/action-interface'

export const resetNewRegistration: ActionIF = ({ commit }): void => {
  commit('mutateNewRegistration')
}

export const setAccountInformation: ActionIF = ({ commit }, account: AccountInformationIF): void => {
  commit('mutateAccountInformation', account)
}

export const setAddCollateral: ActionIF = ({ commit }, addCollateral: AddCollateralIF): void => {
  commit('mutateAddCollateral', addCollateral)
}

export const setAddSecuredPartiesAndDebtors: ActionIF = ({ commit }, addParties: AddPartiesIF): void => {
  commit('mutateAddSecuredPartiesAndDebtors', addParties)
}

export const setAuthRoles: ActionIF = ({ commit }, authRoles: Array<string>): void => {
  commit('mutateAuthRoles', authRoles)
}

export const setCurrentStep: ActionIF = ({ commit }, currentStep): void => {
  commit('mutateCurrentStep', currentStep)
}

export const setDebtorName: ActionIF = ({ commit }, debtorName: IndividualNameIF): void => {
  commit('mutateDebtorName', debtorName)
}

export const setFeeSummary: ActionIF = ({ commit }, feeSummary: FeeSummaryIF): void => {
  commit('mutateFeeSummary', feeSummary)
}

export const setKeycloakRoles: ActionIF = ({ commit }, keycloakRoles): void => {
  commit('mutateKeycloakRoles', keycloakRoles)
}

export const setLengthTrust: ActionIF = ({ commit }, lengthTrust: LengthTrustIF): void => {
  commit('mutateLengthTrust', lengthTrust)
}

export const setRegistrationType: ActionIF = ({ commit }, registrationType: RegistrationTypeIF): void => {
  commit('mutateRegistrationType', registrationType)
}

export const setSearchHistory: ActionIF = ({ commit }, searchHistory: Array<SearchResponseIF>): void => {
  commit('mutateSearchHistory', searchHistory)
}

export const setSearchResults: ActionIF = ({ commit }, searchResults: SearchResponseIF): void => {
  commit('mutateSearchResults', searchResults)
}

export const setSearchedType: ActionIF = ({ commit }, searchedType: SearchTypeIF): void => {
  commit('mutateSearchedType', searchedType)
}

export const setSearchedValue: ActionIF = ({ commit }, searchedValue: string): void => {
  commit('mutateSearchedValue', searchedValue)
}

export const setSearching: ActionIF = ({ commit }, searching: boolean): void => {
  commit('mutateSearching', searching)
}

export const setShowPaymentConfirmation: ActionIF = ({ commit }, showDialog: boolean): void => {
  commit('mutateShowPaymentConfirmation', showDialog)
}

export const setShowSelectConfirmation: ActionIF = ({ commit }, showDialog: boolean): void => {
  commit('mutateShowSelectConfirmation', showDialog)
}

export const setUserInfo: ActionIF = ({ commit }, userInfo: UserInfoIF): void => {
  commit('mutateUserInfo', userInfo)
}

export const setUserSettings: ActionIF = ({ commit }, settings: UserSettingsIF): void => {
  commit('mutateUserSettings', settings)
}

export const setAddSecuredPartiesAndDebtorsStepValidity = ({ commit }, validity) => {
  commit('mutateAddSecuredPartiesAndDebtorsStepValidity', validity)
}

export const setAddCollateralStepValidity = ({ commit }, validity) => {
  commit('mutateAddCollateralStepValidity', validity)
}

export const setLengthTrustStepValidity = ({ commit }, validity) => {
  commit('mutateLengthTrustStepValidity', validity)
}
