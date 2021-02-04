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
