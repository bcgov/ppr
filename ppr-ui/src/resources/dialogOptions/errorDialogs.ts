import { DialogOptionsIF } from '@/interfaces'

export const authPprError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unauthorized access to PPR',
  text: 'This account does not have access to the Personal Property Registry. ' +
  'Please contact us for more information.'
}

export const authAssetsError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unauthorized access to Assets',
  text: 'This account does not have access to the Personal Property Registry or Manufactured Home Registry. ' +
    'Please contact us for more information.'
}

export const draftDeleteError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to delete draft registration',
  text: 'We are unable to delete your draft registration at this time. Please try again later. ' +
  'If this issue persists, please contact us.'
}

export const historyRegError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to retrieve registration history',
  text: 'We were unable to retrieve your registrations. Please try again later. ' +
  'If this issue persists, please contact us.'
}

export const loginError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to retrieve user account information',
  text: 'We are unable to retrieve your Personal Property Registry account information. ' +
  'Please try again later. If this issue persists, please contact us.'
}

export const openDocError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Unable to open document',
  text: 'We are currently unable to open this document. ' +
    'Please try again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const paymentErrorReg: DialogOptionsIF = {
  acceptText: 'Save Draft and Return to Dashboard',
  cancelText: '',
  title: 'Payment Incomplete',
  // filing_type is replaced by the filing type at the time of error
  text: 'The filing_type could not be completed for the following reason:'
}

export const paymentErrorSearch: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Payment Incomplete',
  text: 'The search could not be completed for the following reason:'
}

export const registrationCompleteError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to complete registration',
  text: 'We are unable to complete your registration at this time. Please try to complete this registration later. ' +
    'If this issue persists, please contact us.'
}

export const registrationDeleteError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to remove registration',
  text: 'We are unable to remove your registration at this time. Please try again later. ' +
    'If this issue persists, please contact us.'
}

export const registrationLoadError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to retrieve registration.',
  text: 'Current registration information could not be retrieved. ' +
  'Please try again later. If this issue persists, please contact us.'
}

export const registrationOpenDraftError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to open draft registration',
  text: 'We are currently unable to open your draft registration. ' +
    'Please try again later. If this issue persists, please contact us.'
}

export const registrationSaveDraftError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  hasContactInfo: true,
  title: 'Unable to save draft registration',
  text: 'We are unable to save your draft registration at this time. ' +
    'Please try this again later. If this issue persists, please contact us.'
}

export const searchResultsError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Unable to retrieve search results',
  text: 'Search results could not be retrieved. Your search fee will be refunded. ' +
    'Please try your search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const saveResultsError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Unable to save search results',
  text: 'We are unable to save your search results. Your search fee will be refunded. ' +
    'Please try this search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const saveSelectionsError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Unable to save your selections',
  text: 'We are unable to save your search results. Your search fee will be refunded. ' +
    'Please try this search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const searchReportError: DialogOptionsIF = {
  acceptText: 'Return to Search Results',
  cancelText: 'Return to My PPR Dashboard',
  hasContactInfo: true,
  title: 'Unable to generate a search result report',
  text: 'We were unable to save a PDF search result report because it exceeded ' +
    'the maximum limit of 75 results per report. We are working on removing this ' +
    'limitation so that large PDF reports can be generated. If you require ' +
    'assistance, please contact us.'
}

export const largeSearchReportError: DialogOptionsIF = {
  acceptText: 'Generate Report Now',
  cancelText: 'Change Selected Registrations',
  title: 'Large search result report - confirm selections',
  text: ''
}

export const largeSearchReportDelay: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Large search result report may be delayed',
  text: ''
}

export const cancelOwnerChangeConfirm: DialogOptionsIF = {
  acceptText: 'Cancel Owner Change',
  cancelText: 'Keep Changes',
  title: 'Cancel Transfer Due to Sale or Gift',
  text: 'Cancelling the Transfer Due to Sale or Gift will undo any changes you have made and return you to the ' +
    'original state.'
}

export const changeTransferType: DialogOptionsIF = {
  acceptText: 'Change Transfer Type',
  cancelText: 'Cancel',
  title: 'Change Transfer Type',
  text: 'Changing the Transfer Type will undo any changes you have made and return you to the original state.'
}
