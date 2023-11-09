import { SettingOptions } from '@/enums'
import { UserSettingsIF } from '@/interfaces'
import { mhRegistrationTableHeaders, registrationTableHeaders } from '@/resources'

export const mockedDefaultUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true,
  defaultDropDowns: true,
  defaultTableFilters: true,
  miscellaneousPreferences: [
    {
      accountId: 1,
      qsStatusMsgHide: true,
      successfulRegDialogHide: false
    }
  ]
}

export const mockedDisablePayUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: false,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true,
  defaultDropDowns: true,
  defaultTableFilters: true
}

export const mockedDisableSelectUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: false,
  defaultDropDowns: true,
  defaultTableFilters: true
}

export const mockedDisableAllUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: false,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: false,
  defaultDropDowns: true,
  defaultTableFilters: true
}

export const mockedUpdateRegTableUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true,
  defaultDropDowns: true,
  defaultTableFilters: true,
  [SettingOptions.REGISTRATION_TABLE]: {
    columns: registrationTableHeaders,
    mhrColumns: mhRegistrationTableHeaders
  }
}

export const mockedErrorUserSettingsResponse: UserSettingsIF = {
  [SettingOptions.PAYMENT_CONFIRMATION_DIALOG]: true,
  [SettingOptions.SELECT_CONFIRMATION_DIALOG]: true,
  defaultDropDowns: true,
  defaultTableFilters: true,
  error: {
    statusCode: 500,
    message: 'mocked user settings error.'
  }
}
