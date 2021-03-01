import { AccountInformationIF, SearchResponseIF, StateIF } from '@/interfaces'

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

export const mutateSearching = (state: StateIF, searching: boolean) => {
  state.stateModel.searching = searching
}

export const mutateSearchResults = (state: StateIF, searchResults: SearchResponseIF) => {
  state.stateModel.searchResults = searchResults
}
