import { DialogOptionsIF } from '@/interfaces'

export const registrationAddErrorDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to retrieve existing registrations',
  text: 'We are unable to retrieve existing registrations due to an application ' +
    'error. Please try again later. If this issue persists, please contact us.'
}

export const registrationAlreadyAddedDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Registration Already Added',
  text: '' // added in component (contains dynamic info)
}

export const registrationFoundDialog: DialogOptionsIF = {
  acceptText: 'Add to My Registrations Table',
  cancelText: 'Cancel',
  title: 'Registration Found',
  label: 'a Renewal',
  text: 'The following existing registration was found. Would you like to add ' +
    'it to your registrations table? Adding the base registration to your ' +
    'registrations table will automatically include all associated registrations.',
  textExtra: [] // added in component
}

export const registrationNotFoundDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Registration Not Found',
  text: '' // added in component (contains dynamic info)
}

export const registrationRestrictedDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Restricted Access Registration Found',
  text: '' // added in component (contains dynamic info)
}

export const registrationSaveDraftErrorDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to save draft registration',
  text: 'We are unable to save your draft registration at this time. ' +
    'error. Please try this again later. If this issue persists, please contact us.'
}

export const registrationCompleteErrorDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to complete registration',
  text: 'We are unable to complete your registration at this time. Your draft registration ' +
    'will be saved under "My Registrations". Please try to complete this registration later. ' +
    'If this issue persists, please contact us.'
}

export const registrationOpenDraftErrorDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to open draft registration',
  text: 'We are currently unable to open your draft registration. ' +
    'Please try again later. If this issue persists, please contact us.'
}
