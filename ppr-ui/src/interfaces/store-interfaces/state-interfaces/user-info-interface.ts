import { ContactInfoIF, FeeSettingsIF, UserSettingsIF } from '.'

// User Info state model
export interface UserInfoIF {
  contacts: Array<ContactInfoIF>
  feeSettings: FeeSettingsIF
  firstname: string
  lastname: string
  settings: UserSettingsIF
  username: string
}
