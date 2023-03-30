import { ApiTransferTypes, SupportingDocumentsOptions } from '@/enums'

export const transferSupportingDocuments = {
  [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]: {
    optionOne: {
      text: 'Grant of Probate with Will',
      value: SupportingDocumentsOptions.PROBATE_GRANT,
      note: 'Ensure you have a court certified true copy of the Grant of Probate with the will attached.'
    },
    optionTwo: {
      text: 'Death Certificate',
      value: SupportingDocumentsOptions.DEATH_CERT
    }
  }
}
