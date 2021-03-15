import { SearchResponseIF, SearchTypeIF } from '@/interfaces'
import { ActionIF } from '@/interfaces/store-interfaces/action-interface'

export const setKeycloakRoles: ActionIF = ({ commit }, keycloakRoles): void => {
  commit('mutateKeycloakRoles', keycloakRoles)
}

export const setAuthRoles: ActionIF = ({ commit }, authRoles): void => {
  commit('mutateAuthRoles', authRoles)
}

export const setUserInfo: ActionIF = ({ commit }, userInfo): void => {
  commit('mutateUserInfo', userInfo)
}

export const setAccountInformation: ActionIF = ({ commit }, accountInformation): void => {
  commit('mutateAccountInformation', accountInformation)
}

export const setSearching: ActionIF = ({ commit }, searching: boolean): void => {
  commit('mutateSearching', searching)
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
