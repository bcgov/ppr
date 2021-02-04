import { AccountInformationIF } from '@/interfaces'

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
