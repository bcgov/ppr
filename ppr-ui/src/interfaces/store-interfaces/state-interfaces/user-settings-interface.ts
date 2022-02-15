import { SettingOptions } from '@/enums'
import { BaseHeaderIF, ErrorIF } from '@/interfaces'

// user settings state model
export interface UserSettingsIF {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: boolean // default true
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: boolean // default true
  defaultDropDowns: boolean // default true
  defaultTableFilters: boolean // default true
  [SettingOptions.REGISTRATION_TABLE]?: { columns: BaseHeaderIF[] } // api will save whatever json the UI posts
  miscellaneousPreferences?: any // api will save whatever json the UI posts
  error?: ErrorIF
}
