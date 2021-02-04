// Enums and Interfaces
import { AccountTypes } from '@/enums'

/** Whether the user has "staff" keycloak role. */
export const isRoleStaff = (state: any): boolean => {
  return state.stateModel.tombstone.keycloakRoles.includes('staff')
}

/** Whether the user is authorized to edit. */
export const isAuthEdit = (state: any): boolean => {
  return state.stateModel.tombstone.authRoles.includes('edit')
}

/** Whether the user is authorized to view. */
export const isAuthView = (state: any): boolean => {
  return state.stateModel.tombstone.authRoles.includes('view')
}

/** Whether the current account is a premium account. */
export const isPremiumAccount = (state: any): boolean => {
  return (state.stateModel.accountInformation.accountType === AccountTypes.PREMIUM)
}

/** The current account id. */
export const getAccountId = (state: any): number => {
  return state.stateModel.accountInformation.id
}

/** The current user's email. */
export const getUserEmail = (state: any): string => {
  const userInfo = state.stateModel.tombstone.userInfo
  // get email from contacts[0] if it exists (ie, for BCSC users)
  // else get email from root object
  return userInfo?.contacts[0]?.email || userInfo?.email
}

/** The current user's first name. */
export const getUserFirstName = (state: any): any => {
  return state.stateModel.tombstone.userInfo?.firstname
}

/** The current user's last name. */
export const getUserLastName = (state: any): any => {
  return state.stateModel.tombstone.userInfo?.lastname
}

/** The current user's roles. */
export const getUserRoles = (state: any): any => {
  return state.stateModel.tombstone.userInfo?.roles
}

/** The current user's username. */
export const getUserUsername = (state: any): any => {
  return state.stateModel.tombstone.userInfo?.username
}

/** The staff payment. */
export const getStaffPayment = (state: any): any => {
  return state.stateModel.staffPayment
}
