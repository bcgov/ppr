import { SettingOptions } from '@/enums'
import { BaseHeaderIF, ErrorIF } from '@/interfaces'

// user settings state model
export interface UserSettingsIF {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: boolean // default true
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: boolean // default true
  defaultDropDowns: boolean // default true
  defaultTableFilters: boolean // default true
  // api will save whatever json the UI posts
  [SettingOptions.REGISTRATION_TABLE]?: { columns: BaseHeaderIF[], mhrColumns: BaseHeaderIF[] }
  miscellaneousPreferences?: any // api will save whatever json the UI posts
  error?: ErrorIF
}
