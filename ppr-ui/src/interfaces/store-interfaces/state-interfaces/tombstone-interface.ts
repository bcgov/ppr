import { UserInfoIF } from "./user-info-interface";

// Tombstone State model
export interface TombStoneIF {
  keycloakRoles: Array<string>
  authRoles: Array<string>
  userInfo: UserInfoIF // from auth profile
}
