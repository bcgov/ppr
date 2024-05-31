import { DialogOptionsIF } from '@/interfaces'

export const registrationAddErrorDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to add registration to your table',
  text: 'We are unable to add this registration to your table due to an application ' +
    'error. Please try again later. If this issue persists, please contact us.'
}

export const registrationAlreadyAddedDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Registration Already Added',
  text: '' // added in component (contains dynamic info)
}

// PPR dialog content
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

// MHR dialog content
export const mhRegistrationFoundDialog: DialogOptionsIF = {
  acceptText: 'Add to My Registrations Table',
  cancelText: 'Cancel',
  title: 'Registration Found',
  label: 'a Renewal',
  text: 'The following existing registration was found. Would you like to add ' +
    'it to your registrations table? Adding the MH registration to your ' +
    'registrations table will automatically include all associated registrations.',
  textExtra: [] // added in component
}

// Cancelled MHR dialog content for Qualified Supplier
export const mhRegistrationCannotBeAddedDialog: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Cancelled Registration',
  text: 'The registration for this manufactured home <b>{reg_num}</b> was ' +
    'cancelled and cannot be added to your table. <br><br>You can view the details of this ' +
    'registration by conducting an MHR search for this registration number.'
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
