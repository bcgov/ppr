import { ContactInformationContentIF, ContentIF, RequirementsConfigIF } from '@/interfaces'

export const exDocIdContent: ContentIF = {
  title: 'Document ID',
  sideLabel: 'Document ID',
  description: 'Enter the 8-digit Document ID number.'
}

export const exRemarksContent: ContentIF = {
  title: 'Remarks',
  sideLabel: 'Add Remarks',
  description: 'Remarks will be shown when a search result is produced for this manufactured home.'
}

export const exConfirmRequirements: Array<RequirementsConfigIF> = [
  {
    boldTextPreTooltip: 'An ',
    boldTextPostTooltip: 'will be on this account.',
    underlinedText: 'active B.C. lawyer or notary in good standing',
    tooltipText: 'A practising member in good standing of the Law Society of British Columbia, ' +
      'or a practising member in good standing of the Society of Notaries Public of British Columbia.',
    regularText: 'I understand that only a lawyer or notary, or someone who is being supervised ' +
      'by a lawyer or notary, is authorized to complete Restricted Transactions.'
  },
  {
    boldText: 'All filed documents will be stored for 7 years. ',
    regularText: 'If requested, a copy or certified copy of filed documents ' +
      '(such as the Bill of Sale, or other signed forms), ' +
      'will be provided within 7 business days, at the fee level set by the Registrar.'
  }
]

export const exCertifyInfoContent: ContentIF = {
  title: 'Authorization',
  description: `The following account information will be recorded by BC Registries upon registration and payment. This
   information is used to confirm you have the authority to submit this registration.`,
  sideLabel: 'Confirm Authorization',
  mailAddressInfo: 'Test Address'
}
