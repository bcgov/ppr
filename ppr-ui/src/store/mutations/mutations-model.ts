import {
  AccountInformationIF,
  IndividualNameIF,
  SearchResponseIF,
  SearchTypeIF,
  StateIF,
  UserInfoIF,
  UserSettingsIF
} from '@/interfaces'

export const mutateAccountInformation = (state: StateIF, accountInformation: AccountInformationIF) => {
  state.stateModel.accountInformation = accountInformation
}

export const mutateAuthRoles = (state: StateIF, authRoles: Array<string>) => {
  state.stateModel.authorization.authRoles = authRoles
}

export const mutateDebtorName = (state: StateIF, debtorName: IndividualNameIF) => {
  state.stateModel.debtorName = debtorName
}

export const mutateKeycloakRoles = (state: StateIF, keyCloakRoles: Array<string>) => {
  state.stateModel.authorization.keycloakRoles = keyCloakRoles
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
