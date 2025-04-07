import type { ContactInfoIF, FeeSettingsIF, UserSettingsIF } from '.'

// User Info state model
export interface UserInfoIF {
  id?: string
  contacts: Array<ContactInfoIF>
  feeSettings: FeeSettingsIF
  firstname: string
  lastname: string
  settings: UserSettingsIF
  username: string
}
