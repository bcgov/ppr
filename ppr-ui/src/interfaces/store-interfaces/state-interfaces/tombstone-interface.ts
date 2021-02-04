// Tombstone State model
export interface TombStoneIF {
  keycloakRoles: Array<string>
  authRoles: Array<string>
  userInfo: any // from auth profile
  haveChanges: boolean
}
