import { SettingOptions } from '@/enums'
import { ErrorIF } from '@/interfaces/ppr-api-interfaces'

// user settings state model
export interface UserSettingsIF {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: boolean
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: boolean
  error?: ErrorIF
}
