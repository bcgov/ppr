import { DialogOptionsIF } from '@/interfaces'

export const fetchError: DialogOptionsIF = {
  acceptText: 'Retry',
  cancelText: 'Continue',
  title: 'Retrieve Data Error',
  text: 'We were unable to retrieve your saved data. Please try again later.'
}

export const loginError: DialogOptionsIF = {
  acceptText: 'OK',
  cancelText: '',
  title: 'Unable to retrieve user account information',
  text: 'We are unable to retrieve your Personal Property Registry account information. ' +
  'Please try again later. If this issue persists, please contact us.'
}

export const paymentError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Payment Error',
  text: 'We are unable to process your payment at this time. Please try again later.'
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

export const saveSearchError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Search Error',
  text: 'We were unable to complete this search. Please try again later.'
}

export const searchResultsError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'OK',
  title: 'Unable to retrieve search results',
  text: 'Search results could not be retrieved. Your search fee will be refunded. ' +
    'Please try your search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const saveResultsError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'OK',
  title: 'Unable to save search results',
  text: 'We are unable to save your search results. Your search fee will be refunded. ' +
    'Please try this search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const saveSelectionsError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'OK',
  title: 'Unable to save your selections',
  text: 'We are unable to save your search results. Your search fee will be refunded. ' +
    'Please try this search again later. If this issue persists, please contact us.',
  hasContactInfo: true
}

export const searchPdfError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'OK',
  title: 'Unable to open document',
  text: 'We are currently unable to open this document. ' +
    'Please try again later. If this issue persists, please contact us.',
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
