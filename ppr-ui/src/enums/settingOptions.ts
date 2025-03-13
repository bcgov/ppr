export enum SettingOptions {
  PAYMENT_CONFIRMATION_DIALOG = 'paymentConfirmationDialog',
  SELECT_CONFIRMATION_DIALOG = 'selectConfirmationDialog',
  REGISTRATION_TABLE = 'registrationsTable',
  MISCELLANEOUS_PREFERENCES = 'miscellaneousPreferences',
  QS_STATUS_MSG_HIDE = 'qsStatusMsgHide', // miscellaneousPreferences: Boolean - User has hidden the Qs status msg
  RL_MSG_HIDE = 'rlMsgHide', // miscellaneousPreferences: Boolean - User has hidden the RL msg
  SUCCESSFUL_REGISTRATION_DIALOG_HIDE = 'successfulRegDialogHide' // miscellaneousPreferences: Boolean to disable Registration Successful dialog for future sessions
}
