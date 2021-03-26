import { AccountInformationIF, IndividualNameIF, SearchResponseIF, SearchTypeIF, StateIF } from '@/interfaces'

export const mutateKeycloakRoles = (state: any, keyCloakRoles: Array<string>) => {
  state.stateModel.tombstone.keycloakRoles = keyCloakRoles
}

export const mutateAuthRoles = (state: any, authRoles: Array<string>) => {
  state.stateModel.tombstone.authRoles = authRoles
}

export const mutateUserInfo = (state: any, userInfo: any) => {
  state.stateModel.tombstone.userInfo = userInfo
}

export const mutateAccountInformation = (state: any, accountInformation: AccountInformationIF) => {
  state.stateModel.accountInformation = accountInformation
}

export const mutateDebtorName = (state: StateIF, debtorName: IndividualNameIF) => {
  state.stateModel.debtorName = debtorName
}

export const mutateSearchHistory = (state: StateIF, searchHistory: Array<SearchResponseIF>) => {
  state.stateModel.searchHistory = searchHistory
}

export const mutateSearchResults = (state: StateIF, searchResults: SearchResponseIF) => {
  state.stateModel.searchResults = searchResults
}

export const mutateSearchedType = (state: StateIF, searchedType: SearchTypeIF) => {
  state.stateModel.searchedType = searchedType
}

export const mutateSearchedValue = (state: StateIF, searchedValue: string) => {
  state.stateModel.searchedValue = searchedValue
}
