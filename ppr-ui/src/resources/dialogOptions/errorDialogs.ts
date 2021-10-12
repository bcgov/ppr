import { DialogOptionsIF } from '@/interfaces'

export const fetchError: DialogOptionsIF = {
  acceptText: 'Retry',
  cancelText: 'Continue',
  title: 'Retrieve Data Error',
  text: 'We were unable to retrieve your saved data. Please try again later.'
}

export const loginError: DialogOptionsIF = {
  acceptText: 'Retry',
  cancelText: '',
  title: 'Account Authorization Error',
  text: 'There was an issue logging in to your account. Please try again later.'
}

export const paymentError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Payment Error',
  text: 'We are unable to process your payment at this time. Please try again later.'
}

export const saveSearchError: DialogOptionsIF = {
  acceptText: '',
  cancelText: 'Okay',
  title: 'Search Error',
  text: 'We are unable to complete this search. Please try again later.'
}
