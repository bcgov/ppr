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
