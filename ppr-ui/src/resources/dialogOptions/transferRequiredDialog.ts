import { DialogOptionsIF } from '@/interfaces'

export const transferRequiredDialog: DialogOptionsIF = {
  cancelText: 'Start Transfer Due to Sale or Gift',
  acceptText: 'Complete Later',
  title: 'Your changes have been registered. A Transfer Due to Sale or Gift is now required.',
  label: '',
  // text string is dynamic and mhr_number will be replaced with the MHR number of the Transfer
  text: 'Your Transfer to Executor - Estate under $25,000 with Will for <b>MHR Number mhr_number</b> ' +
  'has been registered. To complete the full transaction, a Transfer Due to Sale or Gift is required.'
}
