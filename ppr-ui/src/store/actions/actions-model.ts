import {
  AccountInformationIF, IndividualNameIF, SearchResponseIF, SearchTypeIF, UserInfoIF, UserSettingsIF
} from '@/interfaces'
import { ActionIF } from '@/interfaces/store-interfaces/action-interface'

export const setAccountInformation: ActionIF = ({ commit }, account: AccountInformationIF): void => {
  commit('mutateAccountInformation', account)
}

export const setAuthRoles: ActionIF = ({ commit }, authRoles: Array<string>): void => {
  commit('mutateAuthRoles', authRoles)
}

export const setDebtorName: ActionIF = ({ commit }, debtorName: IndividualNameIF): void => {
  commit('mutateDebtorName', debtorName)
}

export const setKeycloakRoles: ActionIF = ({ commit }, keycloakRoles): void => {
  commit('mutateKeycloakRoles', keycloakRoles)
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
