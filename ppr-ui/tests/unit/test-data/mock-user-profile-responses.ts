import { SettingOptions } from '@/enums'
import { UserSettingsIF } from '@/interfaces'

export const mockedDefaultUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true
}

export const mockedDisablePayUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: false,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true
}

export const mockedDisableSelectUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: false
}

export const mockedDisableAllUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: false,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: false
}

export const mockedErrorUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true,
  error: {
    statusCode: 500,
    message: 'mocked user settings error.'
  }
}
