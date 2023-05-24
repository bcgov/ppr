import { ApiTransferTypes, HomeOwnerPartyTypes, SupportingDocumentsOptions } from '@/enums'

export const transferSupportingDocumentTypes = {
  [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]: SupportingDocumentsOptions.PROBATE_GRANT,
  [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]: SupportingDocumentsOptions.AFFIDAVIT,
  [ApiTransferTypes.TO_ADMIN_NO_WILL]: SupportingDocumentsOptions.ADMIN_GRANT
}

export const transferOwnerPartyTypes = {
  [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]: HomeOwnerPartyTypes.EXECUTOR,
  [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]: HomeOwnerPartyTypes.EXECUTOR,
  [ApiTransferTypes.TO_ADMIN_NO_WILL]: HomeOwnerPartyTypes.ADMINISTRATOR
}

export const transferOwnerPrefillAdditionalName = {
  [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]: 'Executor of the will of ',
  [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]: 'Executor of the will of ',
  [ApiTransferTypes.TO_ADMIN_NO_WILL]: 'Administrator of the estate of '
}

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
  },
  [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]: {
    optionOne: {
      text: 'Affidavit of Executor with Death Certificate',
      value: SupportingDocumentsOptions.AFFIDAVIT,
      note: 'Ensure you have the original signed Affidavit of Executor form and a ' +
        'court certified true copy of the will.'
    },
    optionTwo: {
      text: 'Death Certificate',
      value: SupportingDocumentsOptions.DEATH_CERT
    }
  },
  [ApiTransferTypes.TO_ADMIN_NO_WILL]: {
    optionOne: {
      text: 'Grant of Administration',
      value: SupportingDocumentsOptions.ADMIN_GRANT,
      note: 'Ensure you have the original court certified true copy of Grant of Administration and ' +
        'Affidavit of Administration with list of Assets and Liabilities.'
    },
    optionTwo: {
      text: 'Death Certificate',
      value: SupportingDocumentsOptions.DEATH_CERT
    }
  }
}
