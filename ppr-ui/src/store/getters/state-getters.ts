// Enums and Interfaces
import { AccountTypes } from '@/enums'
import { IndividualNameIF, SearchResponseIF, SearchTypeIF, StateIF, UserSettingsIF } from '@/interfaces'

/** The current account id. */
export const getAccountId = (state: StateIF): number => {
  return state.stateModel.accountInformation?.id
}

/** The current account label/name. */
export const getAccountLabel = (state: StateIF): string => {
  return state.stateModel.accountInformation?.label
}

/** The search value for ppr search when search type is individual debtor. */
export const getDebtorName = (state: StateIF): IndividualNameIF => {
  return state.stateModel.debtorName
}

/** The api response for ppr search. */
export const getSearchResults = (state: StateIF): SearchResponseIF => {
  return state.stateModel.searchResults
}

/** The selected search type object. */
export const getSearchedType = (state: StateIF): SearchTypeIF => {
  return state.stateModel.searchedType
}

/** The search value for ppr search (unless search type is individual debtor). */
export const getSearchedValue = (state: StateIF): string => {
  return state.stateModel.searchedValue
}

/** The list of past search responses for this account. */
export const getSearchHistory = (state: StateIF): Array<SearchResponseIF> => {
  return state.stateModel.searchHistory
}

/** The current user's email. */
export const getUserEmail = (state: StateIF): string => {
  const userInfo = state.stateModel.userInfo
  return userInfo?.contacts[0]?.email
}

/** The current user's first name. */
export const getUserFirstName = (state: StateIF): string => {
  return state.stateModel.userInfo?.firstname || ''
}

/** The current user's last name. */
export const getUserLastName = (state: StateIF): string => {
  return state.stateModel.userInfo?.lastname || ''
}

/** The current user's roles. */
export const getUserRoles = (state: StateIF): Array<string> => {
  return state.stateModel.authorization?.authRoles
}

/** The current user's roles. */
export const getUserSettings = (state: StateIF): UserSettingsIF => {
  return state.stateModel.userInfo?.settings
}

/** The current user's username. */
export const getUserUsername = (state: StateIF): string => {
  return state.stateModel.userInfo?.username || ''
}

/** Whether the user is authorized to edit. */
export const isAuthEdit = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('edit')
}

/** Whether the user is authorized to view. */
export const isAuthView = (state: StateIF): boolean => {
  return state.stateModel.authorization?.authRoles.includes('view')
}

/** Whether the current account is a premium account. */
export const isPremiumAccount = (state: StateIF): boolean => {
  return (state.stateModel.accountInformation?.accountType === AccountTypes.PREMIUM)
}

/** Whether the user has 'staff' keycloak role. */
export const isRoleStaff = (state: StateIF): boolean => {
  return state.stateModel.authorization?.keycloakRoles.includes('staff')
}

/** Whether the app is processing a search request or not. */
export const isSearching = (state: StateIF): boolean => {
  return state.stateModel.searching
}
