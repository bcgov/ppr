import { DialogOptionsIF } from '@/interfaces'

export const unsavedChangesDialog: DialogOptionsIF = {
  acceptText: 'Return to My Registration',
  cancelText: 'Exit Without Saving',
  title: 'Unsaved Changes',
  label: '',
  text: 'You have unsaved changes. Do you want to return to your registration to ' +
    'save your changes, or exit your registration without saving your changes?'
}

export const notCompleteDialog: DialogOptionsIF = {
  acceptText: 'Return to My Registration',
  cancelText: 'Exit and Discard',
  title: 'Registration Not Complete',
  label: '',
  text: 'Your registration has not been completed. Do you want to exit and discard ' +
    'this registration, or return to your registration and complete it?'
}

export const notCompleteSearchDialog: DialogOptionsIF = {
  acceptText: 'Return to My Search',
  cancelText: 'Exit and Discard',
  title: 'MHR Search Not Complete',
  label: '',
  text: 'Your manufactured home search has not been completed. Do you want to exit and discard ' +
    'this search, or return to complete it?'
}

export const pidNotFoundDialog: DialogOptionsIF = {
  acceptText: 'Retry',
  cancelText: 'Cancel',
  title: 'Unable to retrieve PID number',
  label: '',
  text: 'We were unable to retrieve the PID number. Please try again. If this issue persists please contact us for' +
    'assistance.',
  hasContactInfo: true
}
