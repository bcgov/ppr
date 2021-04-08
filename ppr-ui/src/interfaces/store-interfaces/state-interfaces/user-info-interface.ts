import { UserSettingsIF } from './user-settings-interface'

// User Info state model
export interface UserInfoIF {
  firstname: string
  lastname: string
  username: string
  settings: UserSettingsIF
}
