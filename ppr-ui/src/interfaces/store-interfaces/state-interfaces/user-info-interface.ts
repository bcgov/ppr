import { ContactInfoIF, UserSettingsIF } from '.'

// User Info state model
export interface UserInfoIF {
  contacts: Array<ContactInfoIF>
  firstname: string
  lastname: string
  username: string
  settings: UserSettingsIF
}
