import { DialogOptionsIF } from '@/interfaces'

// error dialogs
export const fetchError = {
  acceptText: 'Retry',
  cancelText: 'Continue',
  title: 'Retrieve Data Error',
  text: 'We were unable to retrieve your saved data. Please try again later.'
}

export const loginError = {
  acceptText: 'Retry',
  cancelText: '',
  title: 'Account Authorization Error',
  text: 'There was an issue logging in to your account. Please try again later.'
}

export const paymentError = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Payment Error',
  text: 'We are unable to process your payment at this time. Please try again later.'
}

export const saveSearchError = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Search Error',
  text: 'We are unable to complete this search. Please try again later.'
}

// confirmation dialogs
export const paymentConfirmaionDialog: DialogOptionsIF = {
  acceptText: 'Accept',
  cancelText: 'Cancel',
  title: 'Payment Confirmation',
  text: 'Each search incurs a fee, even if the search returns no results. ' +
    'Your account will be debited $8.50 for this transaction.'
}

export const selectionConfirmaionDialog = {
  acceptText: 'Accept',
  cancelText: 'Change Selected Registrations',
  title: 'Confirm Selections',
  text: 'registrations will be included in your PDF search results report ' +
    'along with an overview of the search results. Click the <i>Change ' +
    'Selected Registrations</i> button if you would like to edit your ' +
    'selection before returning to the dashboard.'
}

// other registration dialog
export const registrationOtherDialog = {
  acceptText: 'Start Registration',
  cancelText: 'Cancel',
  label: 'Name of Statute',
  title: 'Other Crown Charge Registration',
  text: 'If you need to register a Security Interest under a statute not listed, ' +
    'enter the name of the statute below.'
}

// cancel dialogs
export const dischargeCancelDialog: DialogOptionsIF = {
  acceptText: 'Cancel Total Discharge',
  cancelText: 'Close',
  title: 'Cancel',
  label: '',
  text: 'This will discard all changes made and return you to My Personal Property ' +
    'Registry dashboard.'
}

// discharge cancel
export const renewCancelDialog: DialogOptionsIF = {
  acceptText: 'Cancel Renewal',
  cancelText: 'Close',
  title: 'Cancel',
  label: '',
  text: 'This will discard all changes made and return you to My Personal Property ' +
    'Registry dashboard.'
}

// discharge confirmation
export const dischargeConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be discharged',
  label: 'a Total Discharge',
  text: ''
}

export const amendConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be amended',
  label: 'an Amendment',
  text: ''
}

export const renewConfirmationDialog: DialogOptionsIF = {
  acceptText: 'Continue',
  cancelText: 'Cancel',
  title: 'Confirm registration to be renewed',
  label: 'a Renewal',
  text: ''
}
