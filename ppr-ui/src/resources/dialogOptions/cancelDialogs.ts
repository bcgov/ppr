import type { DialogOptionsIF } from '@/interfaces'

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
  text: 'We were unable to retrieve the PID number. Please try again. If this issue persists please contact us for ' +
    'assistance.',
  hasContactInfo: true
}

export const incompleteApplicationDialog: DialogOptionsIF = {
  acceptText: 'Return to My Application',
  cancelText: 'Exit and Discard',
  title: 'Application Not Complete',
  label: '',
  text: 'Your application has not been completed. Do you want to exit and discard ' +
    'this application, or return to your application and complete it?'
}

export const incompleteRegistrationDialog: DialogOptionsIF = {
  acceptText: 'Return to My Registration',
  cancelText: 'Exit and Discard',
  title: 'Registration Not Complete',
  label: '',
  text: 'Your registration has not been completed. Do you want to exit and discard this registration,' +
    ' or return to your registration and complete it.'
}

export const cancelTransportPermitDialog: DialogOptionsIF = {
  acceptText: 'Cancel Location Change',
  cancelText: 'Keep Changes',
  title: 'Cancel Transport Permit / Location Change',
  label: '',
  text: 'Cancelling the Location Change will undo any changes you have made and return you to the original state.'
}

export const cancelAmendTransportPermitDialog: DialogOptionsIF = {
  acceptText: 'Cancel Location Change',
  cancelText: 'Keep Changes',
  title: 'Cancel Transport Permit Amendment',
  label: '',
  text: 'Cancelling the Transport Permit Amendment will undo any changes you have made and ' +
    'return you to the original state.'
}

export const changeTransportPermitLocationTypeDialog: DialogOptionsIF = {
  acceptText: 'Change Location Type',
  cancelText: 'Cancel',
  title: 'Change Location Type',
  label: '',
  text: 'Changing the Location Type will undo any changes you have made and return you to the original state.'
}

export const confirmNewTransportPermit: DialogOptionsIF = {
  acceptText: 'Confirm and Create New Transport Permit',
  cancelText: 'Back',
  title: 'Verify Transport Permit Status',
  label: '',
  text: 'By applying for a new transport permit you are confirming that the active Transport permit {number} issued' +
    ' on {date of issue} has been completed and will no longer be active.'
}

